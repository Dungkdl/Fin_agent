"""Sinh nhãn (Labeling) cho Dataset."""

import pandas as pd
import numpy as np


class DirectionLabelBuilder:
    def __init__(self, config: dict):
        """
        config map từ file yaml (phần labels:)
        VD: {"positive_threshold": 0.5, "negative_threshold": -0.5, "volatility_window": 48}
        """
        self.config = config
        self.forecast_steps = config.get("forecast_steps", 5) # Default 5 (cho 1d) hoặc 4 (cho 15m)

    def build_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán target (Y) cho mô hình phân loại.
        KHÔNG ĐƯỢC để lọt target này vào tập Features!
        """
        if len(df) == 0:
            return df
            
        df = df.copy()
        close = df["close"]
        
        # 1. Tính future return (DỮ LIỆU TƯƠNG LAI - CHỈ DÙNG ĐỂ TRAINING)
        # return_t = close[t + steps] / close[t] - 1
        df["future_return"] = (close.shift(-self.forecast_steps) / close) - 1
        
        # 2. Lấy label_type từ config
        label_type = self.config.get("label_type", "current")
        window = self.config.get("volatility_window", 48)
        epsilon = 1e-8
        
        # 3. Tính Mẫu số (Denominator) tùy theo label_type
        if label_type == "sqrt_time":
            # L1: sigma_1d * sqrt(horizon)
            log_return_1d = np.log(close / close.shift(1))
            sigma_1d = log_return_1d.rolling(window=window, min_periods=window//2).std()
            denominator = sigma_1d * np.sqrt(self.forecast_steps)
            
        elif label_type == "historical_horizon":
            # L2: historical 5d volatility
            log_return_horizon = np.log(close / close.shift(self.forecast_steps))
            denominator = log_return_horizon.rolling(window=window, min_periods=window//2).std()
            
        else:
            # L0 (current): sigma_1d
            log_return_1d = np.log(close / close.shift(1))
            denominator = log_return_1d.rolling(window=window, min_periods=window//2).std()
        
        # 4. Chuẩn hóa future return
        df["normalized_return"] = df["future_return"] / (denominator + epsilon)
        
        # 5. Gán nhãn (Label)
        pos_thresh = self.config.get("positive_threshold", 0.5)
        neg_thresh = self.config.get("negative_threshold", -0.5)
        
        # Khởi tạo mặc định là sideways
        conditions = [
            df["normalized_return"] > pos_thresh,
            df["normalized_return"] < neg_thresh
        ]
        choices = ["BULLISH", "BEARISH"]
        
        df["direction_label"] = np.select(conditions, choices, default="SIDEWAYS")
        
        # Xóa các dòng bị NaN do shift tương lai (những cây nến cuối cùng không có tương lai để dự đoán)
        # Hàm dataset builder sẽ gọi dropna() ở bước cuối.
        
        return df
