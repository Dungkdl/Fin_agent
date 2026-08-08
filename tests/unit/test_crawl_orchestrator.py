import asyncio
from pathlib import Path

from finsight.crawl.backfill_planner import BackfillRequest
from finsight.crawl.zip_downloader import DownloadResult
from finsight.crawl.crawl_orchestrator import HistoricalIngestionService


class FakeDownloader:
    async def download(self, file, dry_run: bool = False) -> DownloadResult:
        return DownloadResult(
            url=file.url,
            path=Path("data/bronze/fake.zip"),
            checksum_path=Path("data/bronze/fake.zip.CHECKSUM"),
            downloaded=True,
            checksum_valid=True,
        )


class FakeExtractor:
    def extract(self, zip_path: Path, destination: Path) -> list[Path]:
        return [destination / "fake.csv"]


class FakeMetadataWriter:
    def write_metadata(self, symbol: str, interval: str, year: int, month: int, metadata: dict) -> Path:
        assert symbol == "BTCUSDT"
        assert interval == "15m"
        assert year == 2026
        assert month == 1
        assert metadata["checksum_valid"] is True
        return Path("data/bronze/download_metadata.json")


def test_historical_ingestion_service_plans_backfill() -> None:
    request = BackfillRequest.from_cli(
        symbols="BTCUSDT",
        intervals="15m",
        start="2026-01-01",
        end="2026-01-31",
        mode="monthly-zip",
    )

    plan = HistoricalIngestionService().plan_backfill(request)

    assert len(plan.monthly_files) == 1
    assert plan.urls[0].endswith("BTCUSDT/15m/BTCUSDT-15m-2026-01.zip")


from unittest.mock import patch

@patch("finsight.crawl.crawl_orchestrator.parse_kline_csv")
def test_historical_ingestion_service_executes_monthly_zip_plan(mock_parse_csv) -> None:
    mock_parse_csv.return_value = []
    
    async def run() -> None:
        request = BackfillRequest.from_cli(
            symbols="BTCUSDT",
            intervals="15m",
            start="2026-01-01",
            end="2026-01-31",
            mode="monthly-zip",
        )
        service = HistoricalIngestionService(
            downloader=FakeDownloader(),
            extractor=FakeExtractor(),
            metadata_writer=FakeMetadataWriter(),
        )
        plan = service.plan_backfill(request)

        results = await service.ingest_monthly_zip_plan(plan)

        assert len(results) == 1
        assert results[0].download.checksum_valid is True
        assert results[0].extracted_files == (Path("data/bronze/fake.csv"),)

    asyncio.run(run())