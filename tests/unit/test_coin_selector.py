import asyncio

from finsight.crawl.coin_selector import UniverseBuilder


class FakeProvider:
    async def exchange_info(self, symbol: str | None = None) -> dict:
        symbols = [
            symbol_info("BTCUSDT", "BTC", "USDT"),
            symbol_info("ETHUSDT", "ETH", "USDT"),
            symbol_info("SOLUSDT", "SOL", "USDT"),
            symbol_info("BNBUSDT", "BNB", "USDT"),
            symbol_info("XRPUSDT", "XRP", "USDT"),
            symbol_info("ADAUSDT", "ADA", "USDT"),
            symbol_info("DOGEUSDT", "DOGE", "USDT"),
            symbol_info("LINKUSDT", "LINK", "USDT"),
            symbol_info("AVAXUSDT", "AVAX", "USDT"),
            symbol_info("TONUSDT", "TON", "USDT"),
            symbol_info("USDCUSDT", "USDC", "USDT"),
            symbol_info("BTCDOWNUSDT", "BTCDOWN", "USDT"),
            symbol_info("LOWUSDT", "LOW", "USDT"),
            symbol_info("EURBTC", "EUR", "BTC"),
            symbol_info("OLDUSDT", "OLD", "USDT", status="BREAK"),
            symbol_info("NOSPOTUSDT", "NOSPOT", "USDT", spot=False),
        ]
        if symbol:
            symbols = [item for item in symbols if item["symbol"] == symbol]
        return {"symbols": symbols}

    async def ticker_24hr(self, symbol: str | None = None) -> list[dict]:
        tickers = [
            ticker("BTCUSDT", 100_000_000),
            ticker("ETHUSDT", 90_000_000),
            ticker("SOLUSDT", 80_000_000),
            ticker("BNBUSDT", 70_000_000),
            ticker("XRPUSDT", 60_000_000),
            ticker("ADAUSDT", 50_000_000),
            ticker("DOGEUSDT", 40_000_000),
            ticker("LINKUSDT", 1_000),
            ticker("AVAXUSDT", 120_000_000),
            ticker("TONUSDT", 110_000_000),
            ticker("USDCUSDT", 200_000_000),
            ticker("BTCDOWNUSDT", 200_000_000),
            ticker("LOWUSDT", 20_000_000),
            ticker("EURBTC", 300_000_000),
            ticker("OLDUSDT", 300_000_000),
            ticker("NOSPOTUSDT", 300_000_000),
        ]
        if symbol:
            return [item for item in tickers if item["symbol"] == symbol]
        return tickers


def symbol_info(
    symbol: str,
    base_asset: str,
    quote_asset: str,
    status: str = "TRADING",
    spot: bool = True,
) -> dict:
    return {
        "symbol": symbol,
        "status": status,
        "baseAsset": base_asset,
        "quoteAsset": quote_asset,
        "baseAssetPrecision": 8,
        "quoteAssetPrecision": 8,
        "quotePrecision": 8,
        "isSpotTradingAllowed": spot,
        "filters": [],
    }


def ticker(symbol: str, quote_volume: float) -> dict:
    return {
        "symbol": symbol,
        "priceChange": "0",
        "priceChangePercent": "0",
        "weightedAvgPrice": "0",
        "prevClosePrice": "0",
        "lastPrice": "0",
        "bidPrice": "0",
        "askPrice": "0",
        "openPrice": "0",
        "highPrice": "0",
        "lowPrice": "0",
        "volume": "0",
        "quoteVolume": str(quote_volume),
        "count": 1,
    }


def test_universe_builder_keeps_required_and_builds_target_size() -> None:
    async def run() -> None:
        builder = UniverseBuilder(provider=FakeProvider(), min_quote_volume=10_000_000)

        result = await builder.build(limit=10)

        assert result.selected_symbols[:2] == ("BTCUSDT", "ETHUSDT")
        assert len(result.selected_symbols) == 10
        assert "AVAXUSDT" in result.selected_symbols
        assert "TONUSDT" in result.selected_symbols

    asyncio.run(run())


def test_universe_builder_rejects_invalid_symbols_with_reasons() -> None:
    async def run() -> None:
        builder = UniverseBuilder(provider=FakeProvider(), min_quote_volume=10_000_000)

        result = await builder.build(limit=10)
        decisions = {decision.symbol: decision for decision in result.decisions}

        assert decisions["USDCUSDT"].accepted is False
        assert "stablecoin_pair" in decisions["USDCUSDT"].reasons
        assert decisions["BTCDOWNUSDT"].accepted is False
        assert "leveraged_token" in decisions["BTCDOWNUSDT"].reasons
        assert decisions["LINKUSDT"].accepted is False
        assert "quote_volume_below_minimum" in decisions["LINKUSDT"].reasons

    asyncio.run(run())
