"""Schema parse dữ liệu Binance như exchangeInfo và ticker/24hr về kiểu dữ liệu rõ ràng."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BinanceSymbolInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str
    status: str
    base_asset: str = Field(alias="baseAsset")
    quote_asset: str = Field(alias="quoteAsset")
    base_asset_precision: int | None = Field(default=None, alias="baseAssetPrecision")
    quote_asset_precision: int | None = Field(default=None, alias="quoteAssetPrecision")
    quote_precision: int | None = Field(default=None, alias="quotePrecision")
    is_spot_trading_allowed: bool = Field(default=False, alias="isSpotTradingAllowed")
    filters: list[dict] = Field(default_factory=list)


class BinanceTicker24hr(BaseModel):
    model_config = ConfigDict(extra="allow")

    symbol: str
    price_change: float = Field(default=0.0, alias="priceChange")
    price_change_percent: float = Field(default=0.0, alias="priceChangePercent")
    weighted_avg_price: float = Field(default=0.0, alias="weightedAvgPrice")
    prev_close_price: float = Field(default=0.0, alias="prevClosePrice")
    last_price: float = Field(default=0.0, alias="lastPrice")
    bid_price: float = Field(default=0.0, alias="bidPrice")
    ask_price: float = Field(default=0.0, alias="askPrice")
    open_price: float = Field(default=0.0, alias="openPrice")
    high_price: float = Field(default=0.0, alias="highPrice")
    low_price: float = Field(default=0.0, alias="lowPrice")
    volume: float = 0.0
    quote_volume: float = Field(default=0.0, alias="quoteVolume")
    open_time: int | None = Field(default=None, alias="openTime")
    close_time: int | None = Field(default=None, alias="closeTime")
    count: int = 0

    @field_validator(
        "price_change",
        "price_change_percent",
        "weighted_avg_price",
        "prev_close_price",
        "last_price",
        "bid_price",
        "ask_price",
        "open_price",
        "high_price",
        "low_price",
        "volume",
        "quote_volume",
        mode="before",
    )
    @classmethod
    def parse_float(cls, value: object) -> float:
        if value in (None, ""):
            return 0.0
        return float(value)

    @field_validator("count", mode="before")
    @classmethod
    def parse_int(cls, value: object) -> int:
        if value in (None, ""):
            return 0
        return int(value)

