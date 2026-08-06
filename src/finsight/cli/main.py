"""CLI gốc của FinSight. File này chỉ đăng ký các nhóm lệnh như universe và market, không chứa business logic."""

import asyncio
from typing import Annotated

import typer

from finsight.cli.market import app as market_app
from finsight.cli.universe import app as universe_app

app = typer.Typer(help="FinSight Agent command-line tools.")
app.add_typer(universe_app, name="universe")
app.add_typer(market_app, name="market")


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

