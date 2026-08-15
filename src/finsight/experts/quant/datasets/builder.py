"""Pipeline xây dựng Dataset tổng hợp (Gold layer) cho huấn luyện AI."""

import pandas as pd
import logging
from pathlib import Path

from finsight.database.parquet_storage import SilverCandleStorage
from finsight.experts.quant.feature_engineering.features.builder import SharedFeatureBuilder
from finsight.experts.quant.feature_engineering.features.validation import validate_features
from finsight.experts.quant.feature_engineering.labels.direction import DirectionLabelBuilder
from finsight.experts.quant.feature_engineering.weighting.combined import WeightBuilder

logger = logging.getLogger(__name__)


class DatasetBuilder:
    def __init__(
        self, 
        config: dict,
        silver_storage: SilverCandleStorage,
        gold_root: Path = Path("data/gold/training_samples")
    ):
        """
        config là toàn bộ nội dung parse từ file yaml (quant_*.yaml)
        """
        self.config = config
        self.silver_storage = silver_storage
        self.gold_root = gold_root
        
        self.feature_builder = SharedFeatureBuilder(config.get("features", {}))
        self.label_builder = DirectionLabelBuilder(
            {**config.get("labels", {}), "forecast_steps": config.get("forecast_steps", 5)}
        )
        self.weight_builder = WeightBuilder(config.get("weights", {}))

    def build_dataset(self) -> Path:
        """
        Đọc toàn bộ data từ Silver, chạy Feature Engineering, Labeling, Weighting, 
        xóa NaN và lưu thành Parquet ở Gold layer.
        """
        print(f"Building dataset for model: {self.config.get('model_name')}")
        
        symbols = self.config.get("universe", {}).get("required_symbols", ["BTCUSDT", "ETHUSDT"])
        interval = self.config.get("input_interval", "1d")
        
        # 1. Đọc dữ liệu Silver
        # 1. Đọc dữ liệu Silver
        dfs = {sym: self.silver_storage.load_candles("binance", sym, interval) for sym in symbols}
        
        # Lọc bỏ các coin không có data
        dfs = {sym: df for sym, df in dfs.items() if not df.empty}
        if not dfs:
            print("No data found in Silver storage for requested symbols.")
            return None
            
        # 2. Build core features
        for sym, df in dfs.items():
            df = self.feature_builder.build_core_features(df)
            dfs[sym] = df
            
        # 3. Build cross-asset features, labels, and weights
        for sym, df in dfs.items():
            df = self.feature_builder.build_cross_features(df, context_dfs=dfs)
            df = self.label_builder.build_labels(df)
            dfs[sym] = df
            
        # 5. Gom toàn bộ
        combined_df = pd.concat(dfs.values(), ignore_index=True)

        # 4. Gán trọng số
        combined_df = self.weight_builder.build_weights(combined_df)
            
        # 5. Validation - Kiểm định và làm sạch features (Xóa inf, kiểm tra tỷ lệ NaN)
        combined_df = validate_features(combined_df)
            
        # 6. Loại bỏ NaN
        # Tại sao dropna? Vì các hàm rolling window (SMA, MACD, etc.) luôn sinh ra NaN ở các dòng đầu tiên.
        # Tuy nhiên các cột Metadata như source_file có thể bị NaN và làm drop mất toàn bộ dữ liệu. Ta xóa chúng đi trước.
        meta_cols = ["source", "source_file", "quality_status", "quality_flags"]
        combined_df.drop(columns=[c for c in meta_cols if c in combined_df.columns], inplace=True)
        
        combined_df.dropna(inplace=True)
        
        if len(combined_df) == 0:
            print("All rows were dropped during feature/label calculation.")
            return None
            
        out_file = self.gold_root / f"{self.config.get('model_name')}.parquet"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        combined_df.to_parquet(out_file, engine="pyarrow", index=False)
        print(f"Successfully saved {len(combined_df)} samples to {out_file}")
        
        return out_file
