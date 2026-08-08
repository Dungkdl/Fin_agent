"""Helper thời gian UTC dùng chung cho version/report và timestamp."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


def unix_ms_to_utc(timestamp_ms: int) -> datetime:
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)
