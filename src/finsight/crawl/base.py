"""Interface chung cho market data provider. Binance REST client implement interface này để sau này có thể thay provider."""

from abc import ABC, abstractmethod
from typing import Any


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

