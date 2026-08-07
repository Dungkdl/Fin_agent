"""Service điều phối crawl. CLI gọi file này, còn file này nối planner, downloader, extractor và database storage."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from finsight.crawl.backfill_planner import BackfillPlan, BackfillRequest, HistoricalBackfillPlanner
from finsight.crawl.zip_downloader import BulkDownloader, DownloadResult, SafeZipExtractor
from finsight.database.file_storage import BronzeMetadataWriter
from finsight.database.parquet_storage import SilverCandleStorage
from finsight.crawl.candle_validator import CandleValidator, CandleQualityReport
from finsight.crawl.binance.csv_parser import parse_kline_csv
from finsight.crawl.binance.rest_client import BinanceRestClient
from finsight.crawl.rest_downloader import RestBackfillService


@dataclass(frozen=True)
class HistoricalFileIngestionResult:
    download: DownloadResult
    extracted_files: tuple[Path, ...]
    metadata_path: Path
    quality_report: CandleQualityReport | None = None
    silver_path: Path | None = None


@dataclass(frozen=True)
class RestIngestionResult:
    symbol: str
    interval: str
    candles_count: int
    quality_report: CandleQualityReport | None = None
    silver_path: Path | None = None


class HistoricalIngestionService:
    def __init__(
        self,
        planner: HistoricalBackfillPlanner | None = None,
        downloader: BulkDownloader | None = None,
        extractor: SafeZipExtractor | None = None,
        metadata_writer: BronzeMetadataWriter | None = None,
        silver_storage: SilverCandleStorage | None = None,
        validator: CandleValidator | None = None,
    ) -> None:
        self.planner = planner or HistoricalBackfillPlanner()
        self.downloader = downloader or BulkDownloader()
        self.extractor = extractor or SafeZipExtractor()
        self.metadata_writer = metadata_writer or BronzeMetadataWriter()
        self.silver_storage = silver_storage or SilverCandleStorage()
        self.validator = validator or CandleValidator()

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
            
            # Xử lý Silver layer
            all_candles = []
            for csv_file in extracted_files:
                if csv_file.suffix == ".csv":
                    candles = parse_kline_csv(csv_file, file.symbol, file.interval)
                    all_candles.extend(candles)
            
            quality_report = None
            silver_path = None
            if all_candles:
                all_candles = self.validator.deduplicate_candles(all_candles)
                quality_report = self.validator.validate(all_candles, file.interval)
                silver_path = self.silver_storage.save_candles(all_candles)

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
                    "quality_score": quality_report.quality_score if quality_report else 0.0,
                },
            )
            results.append(
                HistoricalFileIngestionResult(
                    download=download,
                    extracted_files=extracted_files,
                    metadata_path=metadata_path,
                    quality_report=quality_report,
                    silver_path=silver_path,
                )
            )
        return tuple(results)

    async def ingest_rest_plan(self, plan: BackfillPlan) -> tuple[RestIngestionResult, ...]:
        results: list[RestIngestionResult] = []
        async with BinanceRestClient() as client:
            rest_service = RestBackfillService(provider=client)
            
            for req in plan.rest_requests:
                candles = await rest_service.fetch(
                    symbol=req.symbol,
                    interval=req.interval,
                    start=req.start,
                    end=req.end,
                )
                
                quality_report = None
                silver_path = None
                if candles:
                    candles = self.validator.deduplicate_candles(candles)
                    quality_report = self.validator.validate(candles, req.interval)
                    silver_path = self.silver_storage.save_candles(candles)

                results.append(
                    RestIngestionResult(
                        symbol=req.symbol,
                        interval=req.interval,
                        candles_count=len(candles),
                        quality_report=quality_report,
                        silver_path=silver_path,
                    )
                )
        return tuple(results)