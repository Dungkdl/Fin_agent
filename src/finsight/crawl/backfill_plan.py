"""Lập kế hoạch tải dữ liệu lịch sử. File này sinh danh sách monthly ZIP cần tải nhưng không download."""

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from finsight.config.crawl_constants import BackfillMode
from finsight.crawl.binance.public_data_client import (
    BinancePublicDataClient,
    BinancePublicDataFile,
)


@dataclass(frozen=True)
class BackfillRequest:
    symbols: tuple[str, ...]
    intervals: tuple[str, ...]
    start: date
    end: date
    mode: BackfillMode = BackfillMode.HYBRID
    dry_run: bool = True

    @classmethod
    def from_cli(
        cls,
        symbols: str,
        intervals: str,
        start: str,
        end: str,
        mode: str,
        dry_run: bool = True,
    ) -> "BackfillRequest":
        start_date = parse_iso_date(start, "start")
        end_date = parse_iso_date(end, "end")
        if end_date < start_date:
            raise ValueError("end must be on or after start")
        return cls(
            symbols=normalize_csv_symbols(symbols),
            intervals=normalize_csv_values(intervals),
            start=start_date,
            end=end_date,
            mode=BackfillMode(mode),
            dry_run=dry_run,
        )


@dataclass(frozen=True)
class BackfillPlan:
    request: BackfillRequest
    monthly_files: tuple[BinancePublicDataFile, ...]

    @property
    def urls(self) -> tuple[str, ...]:
        return tuple(file.url for file in self.monthly_files)


class HistoricalBackfillPlanner:
    def __init__(self, public_data_client: BinancePublicDataClient | None = None) -> None:
        self.public_data_client = public_data_client or BinancePublicDataClient()

    def plan(self, request: BackfillRequest) -> BackfillPlan:
        monthly_files: list[BinancePublicDataFile] = []
        if request.mode in {BackfillMode.MONTHLY_ZIP, BackfillMode.HYBRID}:
            for symbol in request.symbols:
                for interval in request.intervals:
                    monthly_files.extend(self._monthly_files(symbol, interval, request.start, request.end))

        return BackfillPlan(request=request, monthly_files=tuple(monthly_files))

    def _monthly_files(
        self,
        symbol: str,
        interval: str,
        start: date,
        end: date,
    ) -> Iterable[BinancePublicDataFile]:
        current_year = start.year
        current_month = start.month
        while (current_year, current_month) <= (end.year, end.month):
            yield self.public_data_client.monthly_kline_file(
                symbol,
                interval,
                current_year,
                current_month,
            )
            if current_month == 12:
                current_year += 1
                current_month = 1
            else:
                current_month += 1


def parse_iso_date(value: str, name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must use YYYY-MM-DD format") from exc


def normalize_csv_symbols(value: str) -> tuple[str, ...]:
    return tuple(item.strip().upper() for item in value.split(",") if item.strip())


def normalize_csv_values(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())