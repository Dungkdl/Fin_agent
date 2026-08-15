"""Kết hợp các trọng số thành một final_weight duy nhất."""

import pandas as pd
import numpy as np

from finsight.experts.quant.feature_engineering.weighting.class_weight import compute_class_weight
from finsight.experts.quant.feature_engineering.weighting.recency_weight import compute_recency_weight
from finsight.experts.quant.feature_engineering.weighting.regime_weight import compute_regime_weight
from finsight.experts.quant.feature_engineering.weighting.quality_weight import compute_quality_weight


class WeightBuilder:
    def __init__(self, config: dict):
        """
        config map từ file yaml (phần weights:)
        """
        self.config = config

    def build_weights(self, df: pd.DataFrame, target_regime: str = None, reference_time: pd.Timestamp = None) -> pd.DataFrame:
        if len(df) == 0:
            return df
            
        df = df.copy()
        
        # 1. Tính từng thành phần (Bỏ class_weight khỏi đây để tính động trong mỗi fold)
        w_class = 1.0
        w_recency = compute_recency_weight(df, reference_time) if self.config.get("recency_weight", False) else 1.0
        w_regime = compute_regime_weight(df, target_regime) if self.config.get("regime_weight", False) else 1.0
        w_quality = compute_quality_weight(df) if self.config.get("quality_weight", True) else 1.0
        
        # 2. Nhân tất cả lại
        final_weight = w_class * w_recency * w_regime * w_quality
        
        # 3. Clip min/max
        min_w = self.config.get("min_weight", 0.05)
        max_w = self.config.get("max_weight", 5.0)
        final_weight = np.clip(final_weight, min_w, max_w)
        
        # 4. Normalize để mean gần bằng 1 (tùy chọn nhưng giúp learning rate ổn định)
        if final_weight.mean() > 0:
            final_weight = final_weight / final_weight.mean()
            
        # 5. Xử lý NaN/Inf
        final_weight = final_weight.replace([np.inf, -np.inf], np.nan).fillna(min_w)
        
        # Lưu vào dataframe
        df["class_weight"] = w_class
        df["recency_weight"] = w_recency
        df["regime_weight"] = w_regime
        df["quality_weight"] = w_quality
        df["final_weight"] = final_weight
        
        return df
