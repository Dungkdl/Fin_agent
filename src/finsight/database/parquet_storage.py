"""Lưu trữ dữ liệu Silver (Candle) dạng Parquet."""

from pathlib import Path
import pandas as pd

from finsight.domain.data_models import Candle
from finsight.config.crawl_config import StorageConfig


class SilverCandleStorage:
    def __init__(self, config: StorageConfig | None = None) -> None:
        self.config = config or StorageConfig()

    def save_candles(self, candles: list[Candle]) -> Path:
        """Chuyển đổi danh sách Candle thành DataFrame và lưu dạng Parquet phân mảnh."""
        if not candles:
            return self.config.silver_root

        # Chuyển đổi sang DataFrame
        df = pd.DataFrame([c.__dict__ for c in candles])
        
        # Trích xuất year và month để làm partition keys
        df["year"] = df["open_time"].dt.year
        df["month"] = df["open_time"].dt.strftime("%m")  # Giữ định dạng 01, 02...
        
        df["exchange"] = df["exchange"].str.lower()
        df["symbol"] = df["symbol"].str.upper()
        df["interval"] = df["interval"].str.lower()

        # Đảm bảo timezone-aware datetime luôn là UTC
        if df["open_time"].dt.tz is not None:
            df["open_time"] = df["open_time"].dt.tz_convert("UTC")
            df["close_time"] = df["close_time"].dt.tz_convert("UTC")

        # Cột để phân mảnh Parquet
        partition_cols = ["exchange", "symbol", "interval", "year", "month"]
        
        # Thư mục đích
        output_dir = self.config.silver_root

        # Đọc dữ liệu cũ để gộp (upsert) nhằm không bị mất data khi tải REST ghi đè lên ZIP
        if output_dir.exists():
            try:
                old_df = pd.read_parquet(
                    output_dir,
                    engine="pyarrow",
                    filters=[
                        ("exchange", "in", df["exchange"].unique().tolist()),
                        ("symbol", "in", df["symbol"].unique().tolist()),
                        ("interval", "in", df["interval"].unique().tolist()),
                        ("year", "in", df["year"].unique().tolist()),
                        ("month", "in", df["month"].unique().tolist()),
                    ],
                )
                df = pd.concat([old_df, df], ignore_index=True)
                df = df.drop_duplicates(
                    subset=["exchange", "symbol", "interval", "open_time"], 
                    keep="last"
                )
            except Exception:
                pass  # Bỏ qua nếu partition chưa tồn tại hoặc lỗi đọc
        
        # Lưu file, tự động đè lên partition nếu đã tồn tại
        df.to_parquet(
            output_dir,
            engine="pyarrow",
            partition_cols=partition_cols,
            existing_data_behavior="delete_matching",
            index=False,
        )
        
        return output_dir
