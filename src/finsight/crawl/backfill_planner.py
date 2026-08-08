"""Lập kế hoạch tải dữ liệu lịch sử. File này sinh danh sách monthly ZIP cần tải từ CLI truyền vào  nhưng không download."""

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from finsight.domain.enums import BackfillMode
from finsight.crawl.binance.public_data_client import (
    BinancePublicDataClient,
    BinancePublicDataFile,
)

# Định nghĩa các thuộc tính ban đầu từ CLI 
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


from datetime import datetime, timedelta

@dataclass(frozen=True)
class RestRequest:
    symbol: str
    interval: str
    start: datetime
    end: datetime


@dataclass(frozen=True)
class BackfillPlan:
    request: BackfillRequest
    monthly_files: tuple[BinancePublicDataFile, ...]
    rest_requests: tuple[RestRequest, ...] = tuple()

    @property
    def urls(self) -> tuple[str, ...]:
        return tuple(file.url for file in self.monthly_files)


class HistoricalBackfillPlanner:
    def __init__(self, public_data_client: BinancePublicDataClient | None = None) -> None:
        self.public_data_client = public_data_client or BinancePublicDataClient()

    def plan(self, request: BackfillRequest) -> BackfillPlan:
        monthly_files: list[BinancePublicDataFile] = []
        rest_requests: list[RestRequest] = []
        
        # Xác định "tháng hoàn chỉnh gần nhất" so với ngày hiện tại (hôm nay)
        # Vì Binance thường chỉ có file ZIP sau khi kết thúc tháng
        today = datetime.utcnow().date()
        last_complete_month_date = today.replace(day=1) - timedelta(days=1)
        
        for symbol in request.symbols:
            for interval in request.intervals:
                # 1. Tính toán khoảng thời gian cho file ZIP
                if request.mode in {BackfillMode.MONTHLY_ZIP, BackfillMode.HYBRID}:
                    # Chỉ tải ZIP cho những tháng hoàn chỉnh
                    zip_end_date = min(request.end, last_complete_month_date)
                    if request.start <= zip_end_date:
                        monthly_files.extend(
                            self._monthly_files(symbol, interval, request.start, zip_end_date)
                        )
                
                # 2. Tính toán khoảng thời gian cho REST API
                if request.mode in {BackfillMode.REST, BackfillMode.HYBRID}:
                    if request.mode == BackfillMode.REST:
                        # Nếu chế độ thuần REST, tải toàn bộ từ start đến end
                        rest_start_date = request.start
                    else:
                        # Nếu chế độ HYBRID, chỉ lấy REST cho những ngày SAU khi file ZIP kết thúc
                        # Ví dụ: ZIP tải hết tháng 4, thì REST sẽ tải từ 1/5 đến end
                        rest_start_date = max(request.start, last_complete_month_date + timedelta(days=1))
                    
                    if rest_start_date <= request.end:
                        rest_start_dt = datetime.combine(rest_start_date, datetime.min.time())
                        rest_end_dt = datetime.combine(request.end, datetime.max.time())
                        rest_requests.append(RestRequest(
                            symbol=symbol,
                            interval=interval,
                            start=rest_start_dt,
                            end=rest_end_dt,
                        ))

        return BackfillPlan(
            request=request, 
            monthly_files=tuple(monthly_files),
            rest_requests=tuple(rest_requests),
        )
# Tạo ra danh sách các tháng - năm từ start_time  - end_time 
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

# Chuyển CLI ban đầu về đúng định dạng 
def parse_iso_date(value: str, name: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must use YYYY-MM-DD format") from exc

# Normalize về đúng định dạng của symbols 
def normalize_csv_symbols(value: str) -> tuple[str, ...]:
    return tuple(item.strip().upper() for item in value.split(",") if item.strip())


def normalize_csv_values(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())