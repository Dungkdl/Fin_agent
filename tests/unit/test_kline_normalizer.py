from datetime import UTC, datetime

import pytest

from finsight.crawl.binance.normalizer import parse_rest_kline


def sample_row(open_time: int = 1735689600000) -> list:
    return [
        open_time,
        "100.0",
        "110.0",
        "90.0",
        "105.0",
        "12.5",
        open_time + 899999,
        "1312.5",
        42,
        "7.0",
        "735.0",
        "0",
    ]


def test_parse_rest_kline_maps_all_required_fields() -> None:
    candle = parse_rest_kline(sample_row(), symbol="btcusdt", interval="15m")

    assert candle.exchange == "binance"
    assert candle.symbol == "BTCUSDT"
    assert candle.interval == "15m"
    assert candle.open_time == datetime(2025, 1, 1, tzinfo=UTC)
    assert candle.open == 100.0
    assert candle.high == 110.0
    assert candle.low == 90.0
    assert candle.close == 105.0
    assert candle.base_volume == 12.5
    assert candle.quote_volume == 1312.5
    assert candle.trade_count == 42
    assert candle.taker_buy_base_volume == 7.0
    assert candle.taker_buy_quote_volume == 735.0
    assert candle.is_closed is True


def test_parse_rest_kline_rejects_wrong_field_count() -> None:
    with pytest.raises(ValueError, match="12 fields"):
        parse_rest_kline([1, 2, 3], symbol="BTCUSDT", interval="15m")