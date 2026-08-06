"""Binance REST public client. File này gọi ping, time, exchangeInfo, ticker/24hr và klines."""

from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from finsight.config.settings import get_settings
from finsight.crawl.base import MarketDataProvider


class BinanceRestClient(MarketDataProvider):
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.binance_rest_base_url).rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(base_url=self.base_url, timeout=timeout_seconds)

    async def __aenter__(self) -> "BinanceRestClient":
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def ping(self) -> bool:
        await self._get("/api/v3/ping")
        return True

    async def server_time(self) -> int:
        payload = await self._get("/api/v3/time")
        return int(payload["serverTime"])

    async def exchange_info(self, symbol: str | None = None) -> dict[str, Any]:
        params = {"symbol": symbol.upper()} if symbol else None
        return await self._get("/api/v3/exchangeInfo", params=params)

    async def ticker_24hr(self, symbol: str | None = None) -> list[dict[str, Any]]:
        params = {"symbol": symbol.upper()} if symbol else None
        payload = await self._get("/api/v3/ticker/24hr", params=params)
        if isinstance(payload, dict):
            return [payload]
        return payload
    async def klines(
        self,
        symbol: str,
        interval: str,
        start_time_ms: int | None = None,
        end_time_ms: int | None = None,
        limit: int = 1000,
    ) -> list[list[Any]]:
        params: dict[str, Any] = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit,
        }
        if start_time_ms is not None:
            params["startTime"] = start_time_ms
        if end_time_ms is not None:
            params["endTime"] = end_time_ms
        return await self._get("/api/v3/klines", params=params)