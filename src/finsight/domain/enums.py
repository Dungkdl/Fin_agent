"""Enum nghiệp vụ như asset type, exchange và trading mode."""

from enum import StrEnum


class AssetType(StrEnum):
    CRYPTO = "crypto"


class Exchange(StrEnum):
    BINANCE = "binance"


class TradingMode(StrEnum):
    SPOT = "spot"

