import asyncio

import httpx

from finsight.crawl.binance.rest_client import BinanceRestClient


def test_binance_client_uses_exchange_info_symbol_param() -> None:
    async def run() -> None:
        seen_request: httpx.Request | None = None

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal seen_request
            seen_request = request
            return httpx.Response(200, json={"symbols": []})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="https://example.test") as client:
            rest_client = BinanceRestClient(base_url="https://example.test", client=client)
            payload = await rest_client.exchange_info("btcusdt")

        assert payload == {"symbols": []}
        assert seen_request is not None
        assert seen_request.url.path == "/api/v3/exchangeInfo"
        assert seen_request.url.params["symbol"] == "BTCUSDT"

    asyncio.run(run())


def test_binance_client_wraps_single_ticker_payload() -> None:
    async def run() -> None:
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"symbol": "BTCUSDT", "quoteVolume": "100"})

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport, base_url="https://example.test") as client:
            rest_client = BinanceRestClient(base_url="https://example.test", client=client)
            payload = await rest_client.ticker_24hr("BTCUSDT")

        assert payload == [{"symbol": "BTCUSDT", "quoteVolume": "100"}]

    asyncio.run(run())
