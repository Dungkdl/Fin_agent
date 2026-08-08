"""Tính toán Recency weight (Dữ liệu gần đây thì quan trọng hơn)."""

import pandas as pd
import numpy as np


def compute_recency_weight(df: pd.DataFrame, reference_time: pd.Timestamp = None) -> pd.Series:
    """
    reference_time: Thời điểm cuối cùng của fold training. Nếu None, lấy max của close_time.
    Dùng hàm suy giảm hàm mũ (Exponential decay) theo thời gian.
    """
    if len(df) == 0:
        return pd.Series(1.0, index=df.index)
        
    dt_series = pd.to_datetime(df["close_time"])
    
    if reference_time is None:
        reference_time = dt_series.max()
        
    # Tính số ngày chênh lệch (days)
    days_diff = (reference_time - dt_series).dt.total_seconds() / (24 * 3600)
    
    # Những sample tương lai (nếu có nhầm lẫn) hoặc đúng ngày reference sẽ có days_diff <= 0
    days_diff = np.maximum(days_diff, 0)
    
    # Hàm mũ: half-life = 365 ngày (1 năm thì trọng số giảm một nửa)
    half_life_days = 365.0
    decay_rate = np.log(2) / half_life_days
    
    weight = np.exp(-decay_rate * days_diff)
    return pd.Series(weight, index=df.index)
