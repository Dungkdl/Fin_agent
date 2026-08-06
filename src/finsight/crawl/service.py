"""Service điều phối crawl. CLI gọi file này, còn file này nối planner, downloader, extractor và database storage."""

from dataclasses import dataclass
from pathlib import Path

from finsight.crawl.backfill_plan import BackfillPlan, BackfillRequest, HistoricalBackfillPlanner
from finsight.crawl.downloader import BulkDownloader, DownloadResult, SafeZipExtractor
from finsight.database.storage import BronzeMetadataWriter


@dataclass(frozen=True)
class HistoricalFileIngestionResult:
    download: DownloadResult
    extracted_files: tuple[Path, ...]
    metadata_path: Path


class HistoricalIngestionService:
    def __init__(
        self,
        planner: HistoricalBackfillPlanner | None = None,
        downloader: BulkDownloader | None = None,
        extractor: SafeZipExtractor | None = None,
        metadata_writer: BronzeMetadataWriter | None = None,
    ) -> None:
        self.planner = planner or HistoricalBackfillPlanner()
        self.downloader = downloader or BulkDownloader()
        self.extractor = extractor or SafeZipExtractor()
        self.metadata_writer = metadata_writer or BronzeMetadataWriter()

    def plan_backfill(self, request: BackfillRequest) -> BackfillPlan:
        return self.planner.plan(request)

    async def ingest_monthly_zip_plan(
        self,
        plan: BackfillPlan,
    ) -> tuple[HistoricalFileIngestionResult, ...]:
        results: list[HistoricalFileIngestionResult] = []
        for file in plan.monthly_files:
            download = await self.downloader.download(file, dry_run=False)
            extracted_files = tuple(self.extractor.extract(download.path, download.path.parent))
            metadata_path = self.metadata_writer.write_metadata(
                symbol=file.symbol,
                interval=file.interval,
                year=file.year,
                month=file.month,
                metadata={
                    "source_url": file.url,
                    "checksum_url": file.checksum_url,
                    "zip_path": str(download.path),
                    "checksum_path": str(download.checksum_path),
                    "downloaded": download.downloaded,
                    "checksum_valid": download.checksum_valid,
                    "extracted_files": [str(path) for path in extracted_files],
                },
            )
            results.append(
                HistoricalFileIngestionResult(
                    download=download,
                    extracted_files=extracted_files,
                    metadata_path=metadata_path,
                )
            )
        return tuple(results)