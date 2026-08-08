"""Cấu hình runtime đọc từ biến môi trường. Các module khác gọi get_settings() để lấy Binance URL, volume threshold và cấu hình chung."""

from functools import lru_cache
from pathlib import Path
from dataclasses import dataclass

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass(frozen=True)
class BulkDownloadConfig:
    bronze_root: Path = Path("data/bronze/binance/spot/klines")
    timeout_seconds: float = 30.0
    max_retry_attempts: int = 3
    retry_min_seconds: float = 0.5
    retry_max_seconds: float = 8.0


@dataclass(frozen=True)
class RestBackfillConfig:
    limit: int = 1000


@dataclass(frozen=True)
class StorageConfig:
    bronze_root: Path = Path("data/bronze/binance/spot/klines")
    silver_root: Path = Path("data/silver/candles")


@dataclass(frozen=True)
class IngestionConfig:
    bulk_download: BulkDownloadConfig = BulkDownloadConfig()
    rest_backfill: RestBackfillConfig = RestBackfillConfig()
    storage: StorageConfig = StorageConfig()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    finsight_env: str = Field(default="local", alias="FINSIGHT_ENV")
    binance_rest_base_url: str = Field(
        default="https://data-api.binance.vision", alias="BINANCE_REST_BASE_URL"
    )
    universe_min_quote_volume: float = Field(default=10_000_000, alias="UNIVERSE_MIN_QUOTE_VOLUME")
    universe_target_size: int = Field(default=10, alias="UNIVERSE_TARGET_SIZE")
    
    # Cấu hình tĩnh cho module Ingestion
    ingestion: IngestionConfig = IngestionConfig()


@lru_cache
def get_settings() -> Settings:
    return Settings()
