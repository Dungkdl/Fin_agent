"""CLI gốc của FinSight. File này chỉ đăng ký các nhóm lệnh như universe và market, không chứa business logic."""

import asyncio
from typing import Annotated

import typer

from finsight.cli.market_commands import app as market_app
from finsight.cli.universe_commands import app as universe_app
from finsight.cli.quant_commands import app as quant_app

app = typer.Typer(
    help="FinSight Agent CLI. Provides tools for data ingestion, feature engineering, and model training."
)
app.add_typer(universe_app, name="universe", help="Manage Binance trading universes.")
app.add_typer(market_app, name="market", help="Market-data ingestion and validation.")
app.add_typer(quant_app, name="quant", help="Quant ML dataset and training commands.")


def run_async(coro):
    return asyncio.run(coro)


@app.callback()
def main(
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Enable verbose command output."),
    ] = False,
) -> None:
    if verbose:
        typer.echo("Verbose mode enabled.")


if __name__ == "__main__":
    app()

