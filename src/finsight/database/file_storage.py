"""Storage filesystem. File này ghi bronze metadata và silver parquet; sau này database thật cũng nằm trong nhóm database."""

import json
from pathlib import Path
from typing import Any

import pandas as pd

from finsight.domain.data_models import Candle
from finsight.config.settings import StorageConfig
from finsight.config.constants import (
    BRONZE_DOWNLOAD_METADATA_FILENAME,
    DEFAULT_PARQUET_FILENAME,
)


class BronzeMetadataWriter:
    def __init__(self, config: StorageConfig = StorageConfig()) -> None:
        self.config = config

    def write_metadata(
        self,
        symbol: str,
        interval: str,
        year: int,
        month: int,
        metadata: dict[str, Any],
    ) -> Path:
        partition = (
            self.config.bronze_root
            / f"symbol={symbol.upper()}"
            / f"interval={interval}"
            / f"year={year:04d}"
            / f"month={month:02d}"
        )
        partition.mkdir(parents=True, exist_ok=True)
        path = partition / BRONZE_DOWNLOAD_METADATA_FILENAME
        path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
        return path


class SilverCandleWriter:
    def __init__(self, config: StorageConfig = StorageConfig()) -> None:
        self.config = config

    def partition_path(self, candle: Candle) -> Path:
        return (
            self.config.silver_root
            / f"exchange={candle.exchange}"
            / f"symbol={candle.symbol}"
            / f"interval={candle.interval}"
            / f"year={candle.open_time.year:04d}"
            / f"month={candle.open_time.month:02d}"
        )

    def write_parquet(self, candles: list[Candle], filename: str = DEFAULT_PARQUET_FILENAME) -> Path:
        if not candles:
            raise ValueError("Cannot write an empty candle batch")

        first = candles[0]
        partition = self.partition_path(first)
        partition.mkdir(parents=True, exist_ok=True)
        path = partition / filename
        frame = pd.DataFrame([candle_to_record(candle) for candle in candles])
        frame = frame.drop_duplicates(subset=["exchange", "symbol", "interval", "open_time"])
        frame = frame.sort_values(["symbol", "interval", "open_time"])
        frame.to_parquet(path, index=False)
        return path


def candle_to_record(candle: Candle) -> dict[str, Any]:
    return {
        "exchange": candle.exchange,
        "symbol": candle.symbol,
        "interval": candle.interval,
        "open_time": candle.open_time,
        "close_time": candle.close_time,
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "base_volume": candle.base_volume,
        "quote_volume": candle.quote_volume,
        "trade_count": candle.trade_count,
        "taker_buy_base_volume": candle.taker_buy_base_volume,
        "taker_buy_quote_volume": candle.taker_buy_quote_volume,
        "is_closed": candle.is_closed,
        "source": candle.source,
        "source_file": candle.source_file,
        "quality_status": candle.quality_status,
        "quality_flags": list(candle.quality_flags),
    }