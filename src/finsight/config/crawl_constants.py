"""Hằng số riêng cho crawl/ingestion: mode backfill, source type, đường dẫn mặc định, limit và tên file."""

from enum import StrEnum
from pathlib import Path


class BackfillMode(StrEnum):
    MONTHLY_ZIP = "monthly-zip"
    REST = "rest"
    HYBRID = "hybrid"


class IngestionSource(StrEnum):
    MONTHLY_ZIP = "monthly_zip"
    DAILY_ZIP = "daily_zip"
    REST_BACKFILL = "rest_backfill"
    WEBSOCKET = "websocket"
    RECONCILIATION = "reconciliation"


DEFAULT_BRONZE_KLINE_ROOT = Path("data/bronze/binance/spot/klines")
DEFAULT_SILVER_CANDLE_ROOT = Path("data/silver/candles")
DEFAULT_REST_KLINE_LIMIT = 1000
DEFAULT_DOWNLOAD_TIMEOUT_SECONDS = 30.0
DEFAULT_PARQUET_FILENAME = "candles.parquet"
BRONZE_DOWNLOAD_METADATA_FILENAME = "download_metadata.json"
BINANCE_KLINE_FIELD_COUNT = 12