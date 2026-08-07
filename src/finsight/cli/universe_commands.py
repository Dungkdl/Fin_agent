"""CLI cho universe. File này chạy quy trình chọn danh sách coin hợp lệ từ Binance và ghi universe report."""

from typing import Annotated

import typer

from finsight.config.settings import get_settings
from finsight.crawl.coin_selector import UniverseBuilder
from finsight.crawl.universe_exporter import UniverseReportWriter
from finsight.crawl.binance.rest_client import BinanceRestClient

app = typer.Typer(help="Universe management commands.")


@app.command("build")
def build_universe(
    quote_asset: Annotated[str, typer.Option(help="Quote asset to select, usually USDT.")] = "USDT",
    limit: Annotated[int, typer.Option(help="Maximum number of symbols in the universe.")] = 10,
    min_symbols: Annotated[int, typer.Option(help="Minimum acceptable universe size.")] = 8,
    dry_run: Annotated[bool, typer.Option(help="Build the universe without writing a report.")] = False,
) -> None:
    import asyncio

    async def _run() -> None:
        settings = get_settings()
        async with BinanceRestClient() as provider:
            builder = UniverseBuilder(
                provider=provider,
                min_quote_volume=settings.universe_min_quote_volume,
            )
            result = await builder.build(
                quote_asset=quote_asset,
                limit=limit,
                min_symbols=min_symbols,
            )

        typer.echo(f"Universe: {result.universe_name}@{result.version}")
        typer.echo(f"Selected symbols: {', '.join(result.selected_symbols)}")
        if len(result.selected_symbols) < min_symbols:
            raise typer.Exit(code=2)

        if dry_run:
            typer.echo("Dry run: report not written.")
            return

        path = UniverseReportWriter().write(result)
        typer.echo(f"Report written: {path}")

    asyncio.run(_run())

