"""Entity nghiệp vụ dùng chung. Hiện có Candle, là định dạng candle chuẩn mà crawl và quant cùng dùng."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Candle:
    exchange: str
    symbol: str
    interval: str
    open_time: datetime
    close_time: datetime
    open: float
    high: float
    low: float
    close: float
    base_volume: float
    quote_volume: float
    trade_count: int
    taker_buy_base_volume: float
    taker_buy_quote_volume: float
    is_closed: bool
    source: str
    source_file: str | None = None
    quality_status: str = "unknown"
    quality_flags: tuple[str, ...] = field(default_factory=tuple)