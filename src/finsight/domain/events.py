"""Event nghiệp vụ dùng cho realtime hoặc pipeline sau này, ví dụ candle closed event."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CandleClosedEvent:
    symbol: str
    interval: str
    open_time: datetime