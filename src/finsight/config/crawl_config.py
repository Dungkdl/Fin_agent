"""Các config object cho crawl. Downloader, REST backfill và storage nhận config từ đây để tránh hard-code trong logic."""

from dataclasses import dataclass
from pathlib import Path

from finsight.config.crawl_constants import (
    DEFAULT_BRONZE_KLINE_ROOT,
    DEFAULT_DOWNLOAD_TIMEOUT_SECONDS,
    DEFAULT_REST_KLINE_LIMIT,
    DEFAULT_SILVER_CANDLE_ROOT,
)


@dataclass(frozen=True)
class BulkDownloadConfig:
    bronze_root: Path = DEFAULT_BRONZE_KLINE_ROOT
    timeout_seconds: float = DEFAULT_DOWNLOAD_TIMEOUT_SECONDS
    max_retry_attempts: int = 3
    retry_min_seconds: float = 0.5
    retry_max_seconds: float = 8.0


@dataclass(frozen=True)
class RestBackfillConfig:
    limit: int = DEFAULT_REST_KLINE_LIMIT


@dataclass(frozen=True)
class StorageConfig:
    bronze_root: Path = DEFAULT_BRONZE_KLINE_ROOT
    silver_root: Path = DEFAULT_SILVER_CANDLE_ROOT


@dataclass(frozen=True)
class IngestionConfig:
    bulk_download: BulkDownloadConfig = BulkDownloadConfig()
    rest_backfill: RestBackfillConfig = RestBackfillConfig()
    storage: StorageConfig = StorageConfig()