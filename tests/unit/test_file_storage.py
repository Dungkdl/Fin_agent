import shutil
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

from finsight.domain.data_models import Candle
from finsight.config.crawl_config import StorageConfig
from finsight.database.file_storage import BronzeMetadataWriter, SilverCandleWriter


@contextmanager
def workspace_tmp() -> Iterator[Path]:
    path = Path("tmp") / f"test-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def make_candle(offset_minutes: int = 0) -> Candle:
    open_time = datetime(2025, 1, 1, tzinfo=UTC) + timedelta(minutes=offset_minutes)
    return Candle(
        exchange="binance",
        symbol="BTCUSDT",
        interval="15m",
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15) - timedelta(milliseconds=1),
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        base_volume=1.0,
        quote_volume=100.0,
        trade_count=10,
        taker_buy_base_volume=0.5,
        taker_buy_quote_volume=50.0,
        is_closed=True,
        source="test",
        quality_status="valid",
    )


def test_bronze_metadata_writer() -> None:
    with workspace_tmp() as tmp_path:
        path = BronzeMetadataWriter(StorageConfig(bronze_root=tmp_path / "bronze")).write_metadata(
            symbol="btcusdt",
            interval="15m",
            year=2025,
            month=1,
            metadata={"url": "https://example.test/file.zip"},
        )

        assert path.name == "download_metadata.json"
        assert "symbol=BTCUSDT" in str(path)
        assert path.read_text(encoding="utf-8")


def test_silver_candle_writer_writes_partitioned_parquet() -> None:
    with workspace_tmp() as tmp_path:
        path = SilverCandleWriter(StorageConfig(silver_root=tmp_path / "silver")).write_parquet(
            [make_candle(), make_candle(), make_candle(15)]
        )
        frame = pd.read_parquet(path)

        assert path.name == "candles.parquet"
        assert "exchange=binance" in str(path)
        assert len(frame) == 2
        assert list(frame["symbol"].unique()) == ["BTCUSDT"]