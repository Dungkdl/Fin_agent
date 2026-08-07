"""Parser đọc file CSV của Binance klines (từ ZIP)."""

import csv
from pathlib import Path

from finsight.domain.data_models import Candle
from finsight.crawl.binance.normalizer import parse_rest_kline
from finsight.config.crawl_constants import IngestionSource


def parse_kline_csv(csv_path: Path, symbol: str, interval: str) -> list[Candle]:
    """Đọc file CSV klines của Binance và chuyển thành danh sách Candle."""
    candles: list[Candle] = []
    
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) != 12:
                continue
            
            try:
                candle = parse_rest_kline(
                    row=row,
                    symbol=symbol,
                    interval=interval,
                    source=IngestionSource.MONTHLY_ZIP,
                )
                # Lưu thông tin file gốc để truy xuất sau này
                candle = Candle(
                    **{**candle.__dict__, "source_file": csv_path.name}
                )
                candles.append(candle)
            except (ValueError, TypeError):
                # Bỏ qua các dòng lỗi (ví dụ có header)
                pass

    return candles
