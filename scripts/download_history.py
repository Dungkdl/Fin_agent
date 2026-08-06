"""Script wrapper cho command market backfill. Business logic vẫn nằm trong src/finsight."""

from finsight.cli.market import app


if __name__ == "__main__":
    app()