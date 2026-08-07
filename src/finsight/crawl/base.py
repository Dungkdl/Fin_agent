"""Interface chung cho market data provider. Binance REST client implement interface này để sau này có thể thay provider."""

from abc import ABC, abstractmethod
from typing import Any

# File này định nghĩa một interface chung cho market data provider. 
# Nó quy định rằng bất kỳ provider nào muốn được hệ thống sử dụng đều phải có các hàm ping, server_time, exchange_info và ticker_24hr.
class MarketDataProvider(ABC):
    @abstractmethod
    async def ping(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def server_time(self) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exchange_info(self, symbol: str | None = None) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def ticker_24hr(self, symbol: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

