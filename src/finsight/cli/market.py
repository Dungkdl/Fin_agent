"""CLI cho dữ liệu market. File này nhận tham số từ terminal rồi gọi crawl service để lập kế hoạch hoặc tải dữ liệu lịch sử."""

import asyncio
from typing import Annotated

import typer

from finsight.crawl.backfill_plan import BackfillRequest
from finsight.config.crawl_constants import BackfillMode
from finsight.crawl.service import HistoricalIngestionService

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

    if request.dry_run:
        return

    if request.mode not in {BackfillMode.MONTHLY_ZIP, BackfillMode.HYBRID}:
        raise typer.BadParameter("Executable Phase 2 download currently supports monthly-zip or hybrid")

    async def _run() -> None:
        results = await service.ingest_monthly_zip_plan(plan)
        for result in results:
            typer.echo(f"Downloaded: {result.download.path}")
            typer.echo(f"Checksum: {result.download.checksum_path}")
            for extracted in result.extracted_files:
                typer.echo(f"Extracted: {extracted}")
            typer.echo(f"Metadata: {result.metadata_path}")

    asyncio.run(_run())