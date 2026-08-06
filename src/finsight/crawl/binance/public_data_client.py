"""Builder URL Binance Public Data. File này tạo URL monthly/daily ZIP và CHECKSUM."""

from dataclasses import dataclass


BINANCE_PUBLIC_DATA_BASE_URL = "https://data.binance.vision"


@dataclass(frozen=True)
class BinancePublicDataFile:
    symbol: str
    interval: str
    year: int
    month: int
    day: int | None
    url: str
    checksum_url: str
    filename: str


class BinancePublicDataClient:
    def __init__(self, base_url: str = BINANCE_PUBLIC_DATA_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")

    def monthly_kline_file(
        self,
        symbol: str,
        interval: str,
        year: int,
        month: int,
    ) -> BinancePublicDataFile:
        symbol = symbol.upper()
        filename = f"{symbol}-{interval}-{year:04d}-{month:02d}.zip"
        path = f"/data/spot/monthly/klines/{symbol}/{interval}/{filename}"
        url = f"{self.base_url}{path}"
        return BinancePublicDataFile(
            symbol=symbol,
            interval=interval,
            year=year,
            month=month,
            day=None,
            url=url,
            checksum_url=f"{url}.CHECKSUM",
            filename=filename,
        )

    def daily_kline_file(
        self,
        symbol: str,
        interval: str,
        year: int,
        month: int,
        day: int,
    ) -> BinancePublicDataFile:
        symbol = symbol.upper()
        filename = f"{symbol}-{interval}-{year:04d}-{month:02d}-{day:02d}.zip"
        path = f"/data/spot/daily/klines/{symbol}/{interval}/{filename}"
        url = f"{self.base_url}{path}"
        return BinancePublicDataFile(
            symbol=symbol,
            interval=interval,
            year=year,
            month=month,
            day=day,
            url=url,
            checksum_url=f"{url}.CHECKSUM",
            filename=filename,
        )