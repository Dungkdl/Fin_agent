"""CLI cho dữ liệu market. File này nhận tham số từ terminal rồi gọi crawl service để lập kế hoạch hoặc tải dữ liệu lịch sử."""

import asyncio
from typing import Annotated

import typer

from finsight.crawl.backfill_planner import BackfillRequest
from finsight.config.crawl_constants import BackfillMode
from finsight.crawl.crawl_orchestrator import HistoricalIngestionService

app = typer.Typer(help="Market-data ingestion commands.")


@app.command("backfill")
def backfill(
    symbols: Annotated[str, typer.Option(help="Comma-separated symbols, e.g. BTCUSDT,ETHUSDT.")],
    intervals: Annotated[str, typer.Option(help="Comma-separated intervals, e.g. 15m,1h.")],
    start: Annotated[str, typer.Option(help="Start date in YYYY-MM-DD format.")],
    end: Annotated[str, typer.Option(help="End date in YYYY-MM-DD format.")],
    mode: Annotated[str, typer.Option(help="Backfill mode: monthly-zip, rest, or hybrid.")] = "hybrid",
    dry_run: Annotated[bool, typer.Option(help="Print planned files without downloading.")] = True,
) -> None:
    try:
        request = BackfillRequest.from_cli(
            symbols=symbols,
            intervals=intervals,
            start=start,
            end=end,
            mode=mode,
            dry_run=dry_run,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    service = HistoricalIngestionService()
    plan = service.plan_backfill(request)
    typer.echo(f"Backfill plan mode={request.mode} dry_run={request.dry_run}")
    for url in plan.urls:
        typer.echo(url)
    for req in plan.rest_requests:
        typer.echo(f"REST API: {req.symbol} {req.interval} from {req.start} to {req.end}")

    if request.dry_run:
        return

    async def _run() -> None:
        if plan.monthly_files:
            typer.echo("\n[1/2] Processing Monthly ZIPs...")
            zip_results = await service.ingest_monthly_zip_plan(plan)
            for result in zip_results:
                typer.echo(f"Downloaded: {result.download.path}")
                if result.silver_path:
                    typer.echo(f"Saved to Silver: {result.silver_path}")
                if result.quality_report:
                    typer.echo(
                        f"Quality Score: {result.quality_report.quality_score:.2%} "
                        f"| Total: {result.quality_report.total_rows} "
                        f"| Missing: {result.quality_report.missing_candles} "
                        f"| Duplicates: {result.quality_report.duplicate_rows}"
                    )
        
        if plan.rest_requests:
            typer.echo("\n[2/2] Processing REST Incremental...")
            rest_results = await service.ingest_rest_plan(plan)
            for result in rest_results:
                typer.echo(f"Fetched REST: {result.symbol} {result.interval} ({result.candles_count} candles)")
                if result.silver_path:
                    typer.echo(f"Saved to Silver: {result.silver_path}")
                if result.quality_report:
                    typer.echo(
                        f"Quality Score: {result.quality_report.quality_score:.2%} "
                        f"| Total: {result.quality_report.total_rows} "
                        f"| Missing: {result.quality_report.missing_candles} "
                        f"| Duplicates: {result.quality_report.duplicate_rows}"
                    )
                    
        typer.echo("\nDone!")

    try:
        asyncio.run(_run())
    except UnicodeEncodeError:
        # Nếu Windows PowerShell bị lỗi không hiển thị được đường dẫn có tiếng Việt
        typer.echo("Data saved successfully, but terminal cannot display paths with accents.")
        typer.echo("Please set $env:PYTHONIOENCODING='utf-8' before running next time.")