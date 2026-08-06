"""Entrypoint worker. Sau này dùng cho realtime stream, reconciliation và scheduled jobs."""

from finsight.config.logging import configure_logging


def main() -> None:
    configure_logging()
    print("FinSight worker entrypoint is ready. Realtime jobs are implemented in a later phase.")


if __name__ == "__main__":
    main()