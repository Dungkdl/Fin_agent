import asyncio
from datetime import UTC, datetime

from finsight.config.settings import RestBackfillConfig
from finsight.crawl.rest_downloader import RestBackfillService


class FakeKlineProvider:
    def __init__(self) -> None:
        self.calls = []

    async def klines(
        self,
        symbol: str,
        interval: str,
        start_time_ms: int | None = None,
        end_time_ms: int | None = None,
        limit: int = 1000,
    ) -> list[list]:
        self.calls.append((symbol, interval, start_time_ms, end_time_ms, limit))
        if len(self.calls) == 1:
            return [row(1735689600000), row(1735690500000)]
        return [row(1735691400000)]


def row(open_time: int) -> list:
    return [
        open_time,
        "100",
        "110",
        "90",
        "105",
        "1",
        open_time + 899999,
        "100",
        10,
        "0.5",
        "50",
        "0",
    ]


def test_rest_backfill_paginates_until_short_page() -> None:
    async def run() -> None:
        provider = FakeKlineProvider()
        service = RestBackfillService(provider=provider, config=RestBackfillConfig(limit=2))

        candles = await service.fetch(
            symbol="BTCUSDT",
            interval="15m",
            start=datetime(2025, 1, 1, tzinfo=UTC),
            end=datetime(2025, 1, 1, 1, tzinfo=UTC),
        )

        assert len(candles) == 3
        assert len(provider.calls) == 2
        assert provider.calls[1][2] == 1735690500001

    asyncio.run(run())