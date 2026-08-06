"""Parser timestamp Binance. Tự nhận biết seconds, milliseconds hoặc microseconds rồi chuyển sang UTC datetime."""

from datetime import UTC, datetime


def parse_binance_timestamp(value: int | str) -> datetime:
    timestamp = int(value)
    magnitude = abs(timestamp)

    if magnitude >= 10**15:
        seconds = timestamp / 1_000_000
    elif magnitude >= 10**12:
        seconds = timestamp / 1_000
    else:
        seconds = timestamp

    return datetime.fromtimestamp(seconds, tz=UTC)

