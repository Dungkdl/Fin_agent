"""Cấu hình runtime đọc từ biến môi trường. Các module khác gọi get_settings() để lấy Binance URL, volume threshold và cấu hình chung."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    finsight_env: str = Field(default="local", alias="FINSIGHT_ENV")
    binance_rest_base_url: str = Field(
        default="https://data-api.binance.vision", alias="BINANCE_REST_BASE_URL"
    )
    universe_min_quote_volume: float = Field(default=10_000_000, alias="UNIVERSE_MIN_QUOTE_VOLUME")
    universe_target_size: int = Field(default=10, alias="UNIVERSE_TARGET_SIZE")


@lru_cache
def get_settings() -> Settings:
    return Settings()

