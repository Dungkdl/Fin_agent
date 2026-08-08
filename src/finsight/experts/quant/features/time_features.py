"""Tính toán các đặc trưng chu kỳ thời gian (Time Cyclical Features)."""

import pandas as pd
import numpy as np


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # Sử dụng close_time vì nó đại diện cho thời điểm chốt cây nến (feature_time)
    dt_series = pd.to_datetime(df["close_time"])
    
    # Giờ trong ngày (0-23)
    hours = dt_series.dt.hour + (dt_series.dt.minute / 60.0)
    df["hour_sin"] = np.sin(2 * np.pi * hours / 24.0)
    df["hour_cos"] = np.cos(2 * np.pi * hours / 24.0)
    
    # Ngày trong tuần (0=Thứ 2, 6=Chủ Nhật)
    days = dt_series.dt.dayofweek
    df["day_of_week_sin"] = np.sin(2 * np.pi * days / 7.0)
    df["day_of_week_cos"] = np.cos(2 * np.pi * days / 7.0)
    
    # Cờ cuối tuần (Thứ 7 và Chủ Nhật)
    df["weekend_flag"] = days.isin([5, 6]).astype(int)
    
    return df
