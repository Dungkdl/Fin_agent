"""Kiểm tra chất lượng candle: duplicate, missing candle, OHLC sai, volume âm và timestamp lỗi."""

from dataclasses import dataclass
from datetime import timedelta

from finsight.domain.entities import Candle


INTERVAL_DELTAS = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
    "1w": timedelta(weeks=1),
}


@dataclass(frozen=True)
class CandleQualityReport:
    total_rows: int
    duplicate_rows: int
    missing_candles: int
    invalid_ohlc_rows: int
    negative_volume_rows: int
    null_rows: int
    timestamp_errors: int
    quality_score: float
    details: dict


class CandleValidator:
    def validate(self, candles: list[Candle], interval: str) -> CandleQualityReport:
        if interval not in INTERVAL_DELTAS:
            raise ValueError(f"Unsupported interval: {interval}")

        duplicate_rows = self.count_duplicates(candles)
        invalid_ohlc_rows = sum(1 for candle in candles if not self.is_valid_ohlc(candle))
        negative_volume_rows = sum(1 for candle in candles if self.has_negative_volume(candle))
        timestamp_errors = sum(1 for candle in candles if candle.close_time <= candle.open_time)
        missing_candles = self.count_missing_candles(candles, interval)
        null_rows = 0
        total_rows = len(candles)
        issue_count = (
            duplicate_rows
            + invalid_ohlc_rows
            + negative_volume_rows
            + timestamp_errors
            + missing_candles
            + null_rows
        )
        denominator = max(total_rows + missing_candles, 1)
        quality_score = max(0.0, 1.0 - issue_count / denominator)

        return CandleQualityReport(
            total_rows=total_rows,
            duplicate_rows=duplicate_rows,
            missing_candles=missing_candles,
            invalid_ohlc_rows=invalid_ohlc_rows,
            negative_volume_rows=negative_volume_rows,
            null_rows=null_rows,
            timestamp_errors=timestamp_errors,
            quality_score=quality_score,
            details={"interval": interval},
        )

    def is_valid_ohlc(self, candle: Candle) -> bool:
        return (
            candle.high >= candle.low
            and candle.high >= candle.open
            and candle.high >= candle.close
            and candle.low <= candle.open
            and candle.low <= candle.close
        )

    def has_negative_volume(self, candle: Candle) -> bool:
        return (
            candle.base_volume < 0
            or candle.quote_volume < 0
            or candle.trade_count < 0
            or candle.taker_buy_base_volume < 0
            or candle.taker_buy_quote_volume < 0
        )

    def count_duplicates(self, candles: list[Candle]) -> int:
        seen: set[tuple[str, str, object]] = set()
        duplicates = 0
        for candle in candles:
            key = (candle.symbol, candle.interval, candle.open_time)
            if key in seen:
                duplicates += 1
            seen.add(key)
        return duplicates

    def count_missing_candles(self, candles: list[Candle], interval: str) -> int:
        if len(candles) < 2:
            return 0
        delta = INTERVAL_DELTAS[interval]
        ordered = sorted(candles, key=lambda candle: candle.open_time)
        missing = 0
        for previous, current in zip(ordered, ordered[1:], strict=False):
            gap = current.open_time - previous.open_time
            if gap > delta:
                missing += int(gap / delta) - 1
        return missing