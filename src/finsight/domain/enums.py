"""Enum nghiệp vụ như asset type, exchange và trading mode.Định nghĩ các giá trị hợp lệ """

from enum import StrEnum


class AssetType(StrEnum):
    CRYPTO = "crypto"


class Exchange(StrEnum):
    BINANCE = "binance"


class TradingMode(StrEnum):
    SPOT = "spot"


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
