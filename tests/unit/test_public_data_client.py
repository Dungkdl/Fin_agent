from finsight.crawl.binance.public_data_client import BinancePublicDataClient


def test_monthly_kline_url_builder() -> None:
    client = BinancePublicDataClient()

    file = client.monthly_kline_file("btcusdt", "15m", 2026, 1)

    assert file.url == (
        "https://data.binance.vision/data/spot/monthly/klines/"
        "BTCUSDT/15m/BTCUSDT-15m-2026-01.zip"
    )
    assert file.checksum_url == f"{file.url}.CHECKSUM"
    assert file.filename == "BTCUSDT-15m-2026-01.zip"


def test_daily_kline_url_builder() -> None:
    client = BinancePublicDataClient()

    file = client.daily_kline_file("ethusdt", "1h", 2026, 3, 9)

    assert file.url.endswith("/ETHUSDT/1h/ETHUSDT-1h-2026-03-09.zip")
    assert file.checksum_url.endswith(".zip.CHECKSUM")