from datetime import UTC, datetime, timedelta

from finsight.domain.entities import Candle
from finsight.crawl.validator import CandleValidator


def make_candle(offset_minutes: int, **overrides) -> Candle:
    open_time = datetime(2025, 1, 1, tzinfo=UTC) + timedelta(minutes=offset_minutes)
    values = {
        "exchange": "binance",
        "symbol": "BTCUSDT",
        "interval": "15m",
        "open_time": open_time,
        "close_time": open_time + timedelta(minutes=15) - timedelta(milliseconds=1),
        "open": 100.0,
        "high": 110.0,
        "low": 90.0,
        "close": 105.0,
        "base_volume": 1.0,
        "quote_volume": 100.0,
        "trade_count": 10,
        "taker_buy_base_volume": 0.5,
        "taker_buy_quote_volume": 50.0,
        "is_closed": True,
        "source": "test",
    }
    values.update(overrides)
    return Candle(**values)


def test_validator_counts_duplicates_missing_and_invalid_rows() -> None:
    candles = [
        make_candle(0),
        make_candle(0),
        make_candle(30, high=80.0),
        make_candle(45, base_volume=-1.0),
    ]

    report = CandleValidator().validate(candles, interval="15m")

    assert report.total_rows == 4
    assert report.duplicate_rows == 1
    assert report.missing_candles == 1
    assert report.invalid_ohlc_rows == 1
    assert report.negative_volume_rows == 1
    assert report.quality_score < 1.0