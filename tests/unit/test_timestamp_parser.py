from datetime import UTC, datetime

from finsight.crawl.binance.timestamp_parser import parse_binance_timestamp


def test_parse_millisecond_timestamp() -> None:
    parsed = parse_binance_timestamp(1735689600000)

    assert parsed == datetime(2025, 1, 1, tzinfo=UTC)


def test_parse_microsecond_timestamp() -> None:
    parsed = parse_binance_timestamp(1735689600000000)

    assert parsed == datetime(2025, 1, 1, tzinfo=UTC)

