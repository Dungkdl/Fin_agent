"""REST backfill cho Binance klines. Dùng để lấy dữ liệu incremental qua /api/v3/klines và normalize thành Candle."""

from datetime import datetime
from typing import Protocol

from finsight.domain.data_models import Candle
from finsight.config.crawl_config import RestBackfillConfig
from finsight.config.crawl_constants import IngestionSource
from finsight.crawl.binance.normalizer import parse_rest_kline


class KlineProvider(Protocol):
    async def klines(
        self,
        symbol: str,
        interval: str,
        start_time_ms: int | None = None,
        end_time_ms: int | None = None,
        limit: int = 1000,
    ) -> list[list]: ...


def datetime_to_unix_ms(value: datetime) -> int:
    return int(value.timestamp() * 1000)


class RestBackfillService:
    def __init__(
        self,
        provider: KlineProvider,
        config: RestBackfillConfig = RestBackfillConfig(),
    ) -> None:
        self.provider = provider
        self.config = config

    async def fetch(
        self,
        symbol: str,
        interval: str,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        start_ms = datetime_to_unix_ms(start)
        end_ms = datetime_to_unix_ms(end)
        candles: list[Candle] = []

        while start_ms <= end_ms:
            rows = await self.provider.klines(
                symbol=symbol,
                interval=interval,
                start_time_ms=start_ms,
                end_time_ms=end_ms,
                limit=self.config.limit,
            )
            if not rows:
                break

            parsed = [
                parse_rest_kline(
                    row,
                    symbol=symbol,
                    interval=interval,
                    source=IngestionSource.REST_BACKFILL,
                )
                for row in rows
            ]
            candles.extend(parsed)
            last_open_ms = int(rows[-1][0])
            next_start_ms = last_open_ms + 1
            if next_start_ms <= start_ms:
                break
            start_ms = next_start_ms

            if len(rows) < self.config.limit:
                break

        return candles