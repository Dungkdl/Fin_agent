"""Tính toán Quality weight (Phạt trọng số cho các nến bị lỗi/thiếu data)."""

import pandas as pd


def compute_quality_weight(df: pd.DataFrame) -> pd.Series:
    """
    Dựa trên chất lượng dữ liệu để giảm trọng số.
    Nếu trade_count == 0 hoặc volume == 0 -> giảm trọng số mạnh.
    """
    if len(df) == 0:
        return pd.Series(1.0, index=df.index)
        
    weight = pd.Series(1.0, index=df.index)
    
    # Phạt các cây nến không có giao dịch
    is_zero_volume = (df["base_volume"] == 0) | (df["trade_count"] == 0)
    weight.loc[is_zero_volume] = 0.1
    
    # Phạt các cây nến có giá trị High/Low bất thường (ví dụ High < Low, dù SilverStorage đã chặn một phần)
    is_invalid_ohlc = (df["high"] < df["low"]) | (df["high"] < df["open"]) | (df["high"] < df["close"])
    weight.loc[is_invalid_ohlc] = 0.0
    
    return weight
