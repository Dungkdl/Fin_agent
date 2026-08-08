"""Pipeline điều phối quá trình huấn luyện và đánh giá mô hình."""

import pandas as pd
import logging
from pathlib import Path
import warnings

from finsight.experts.quant.models.lightgbm_model import LightGBMQuantModel
from finsight.experts.quant.models.splitters.walk_forward import WalkForwardSplitter

logger = logging.getLogger(__name__)

class TrainingPipeline:
    def __init__(self, config: dict, data_path: Path):
        self.config = config
        self.data_path = Path(data_path)
        
        # Parse configs
        val_config = config.get("validation", {})
        self.min_train_months = val_config.get("min_train_months", 12)
        self.validation_months = val_config.get("validation_months", 3)
        self.step_months = val_config.get("step_months", 3)
        self.final_holdout_months = val_config.get("final_holdout_months", 3)
        
        # Sử dụng LightGBM mặc định
        self.model = LightGBMQuantModel(config.get("model", {}))
        
        # Khởi tạo splitter, forecast_horizon = embargo_steps (quy đổi tương đối, giả sử 5 nến = 5)
        # Trong thực tế, embargo_steps phải đổi từ time string (e.g. "5d") sang số nến hoặc dùng date offset.
        # Ở đây ta giả định embargo = forecast_steps từ config
        self.embargo_steps = config.get("forecast_steps", 5)
        self.splitter = WalkForwardSplitter(
            min_train_months=self.min_train_months,
            validation_months=self.validation_months,
            step_months=self.step_months,
            embargo_steps=self.embargo_steps
        )

    def run(self):
        logger.info(f"Đọc dữ liệu từ {self.data_path}")
        df = pd.read_parquet(self.data_path)
        df = df.sort_values("close_time").reset_index(drop=True)
        
        # 1. Tách Final Holdout (Tập dữ liệu tối mật, không được dùng để Tuning)
        end_time = df["close_time"].max()
        holdout_start = end_time - pd.DateOffset(months=self.final_holdout_months)
        
        # Embargo cho Holdout
        # Chắc chắn rằng tập Holdout không bị rò rỉ label từ tập Train.
        # Tìm nến cuối cùng của tập Train bằng cách lùi lại embargo_steps từ holdout_start
        holdout_mask = df["close_time"] >= holdout_start
        holdout_idx = df.index[holdout_mask]
        
        if len(holdout_idx) > 0:
            first_holdout_idx = holdout_idx[0]
            train_end_idx = first_holdout_idx - self.embargo_steps
            train_time_limit = df["close_time"].iloc[train_end_idx]
            
            df_train_val = df[df["close_time"] <= train_time_limit].copy()
            df_holdout = df[holdout_mask].copy()
            logger.info(f"Tách Final Holdout: {len(df_holdout)} samples. Train/Val: {len(df_train_val)} samples.")
        else:
            warnings.warn("Không đủ dữ liệu để tạo Final Holdout!")
            df_train_val = df.copy()
            df_holdout = pd.DataFrame()
            
        # 2. Huấn luyện mô hình (Bao gồm Optuna Tuning qua CV)
        logger.info("Bắt đầu huấn luyện mô hình với Walk-Forward CV...")
        self.model.train(df_train_val, cv_splitter=self.splitter)
        
        # 3. Lưu mô hình
        model_dir = f"artifacts/models/crypto/{self.config.get('model_name', 'default_model')}/v1"
        logger.info(f"Lưu mô hình tại {model_dir}")
        self.model.save(model_dir)
        
        # 4. Đánh giá sơ bộ trên Holdout (Nếu có)
        if not df_holdout.empty:
            preds = self.model.predict(df_holdout)
            accuracy = (preds == df_holdout["direction_label"]).mean()
            logger.info(f"Accuracy trên Final Holdout: {accuracy:.2%}")
        
        return model_dir
