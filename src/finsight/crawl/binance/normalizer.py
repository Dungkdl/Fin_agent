"""Normalizer Binance kline. File này chuyển row 12 field của Binance thành Candle chuẩn nội bộ."""

from collections.abc import Sequence
from typing import Any

from finsight.domain.entities import Candle
from finsight.crawl.binance.timestamp_parser import parse_binance_timestamp


def parse_rest_kline(
    row: Sequence[Any],
    symbol: str,
    interval: str,
    source: str = "rest_backfill",
) -> Candle:
    if len(row) != 12:
        raise ValueError(f"Expected Binance kline row with 12 fields, got {len(row)}")

    return Candle(
        exchange="binance",
        symbol=symbol.upper(),
        interval=interval,
        open_time=parse_binance_timestamp(row[0]),
        open=float(row[1]),
        high=float(row[2]),
        low=float(row[3]),
        close=float(row[4]),
        base_volume=float(row[5]),
        close_time=parse_binance_timestamp(row[6]),
        quote_volume=float(row[7]),
        trade_count=int(row[8]),
        taker_buy_base_volume=float(row[9]),
        taker_buy_quote_volume=float(row[10]),
        is_closed=True,
        source=source,
    )