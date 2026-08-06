"""Enum nghiệp vụ như asset type, exchange và trading mode.Định nghĩ các giá trị hợp lệ """

from enum import StrEnum


class AssetType(StrEnum):
    CRYPTO = "crypto"


class Exchange(StrEnum):
    BINANCE = "binance"


class TradingMode(StrEnum):
    SPOT = "spot"

