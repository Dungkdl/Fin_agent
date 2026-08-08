"""Tính toán thêm các chỉ số về giá."""

import numpy as np
import pandas as pd


def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]
    open_p = df["open"]

    # 1. Returns (Tỷ suất sinh lời): 
    # Đo lường phần trăm thay đổi giá sau N chu kỳ nến.
    # Ý nghĩa: Giúp AI hiểu được đà tăng/giảm ngắn hạn và trung hạn.
    for period in [1, 2, 4, 8, 16]:
        df[f"return_{period}"] = close.pct_change(periods=period)

    # 2. Log return (Tỷ suất sinh lời logarit):
    # Ý nghĩa: Thường được chuộng trong mô hình tài chính hơn pct_change vì nó có tính chất cộng dồn (additive) và phân phối đối xứng hơn.
    df["log_return_1"] = np.log(close / close.shift(1))

    # 3. Ranges (Biên độ giá):
    # Đo lường sức mạnh và độ biến động trong chính phiên giao dịch (cây nến) đó.
    epsilon = 1e-8
    df["high_low_range"] = (high - low) / (close + epsilon)               # Nến càng dài (từ đỉnh đến đáy) thì thị trường càng biến động mạnh.
    df["close_open_range"] = (close - open_p) / (open_p + epsilon)        # Nến thân đặc (xanh/đỏ) dài thể hiện phe Mua/Bán đang áp đảo.
    df["close_position_in_range"] = (close - low) / (high - low + epsilon) # Vị trí giá đóng cửa so với toàn bộ nến. Gần 1 là đóng ở đỉnh (Bullish), gần 0 là đóng ở đáy (Bearish).

    # 4. Rolling distance (Khoảng cách so với đỉnh/đáy cục bộ):
    # Ý nghĩa: Phát hiện giá đang ở vùng quá mua (gần đỉnh) hay quá bán (gần đáy) trong 20 nến qua.
    rolling_20_high = high.rolling(window=20, min_periods=10).max()
    rolling_20_low = low.rolling(window=20, min_periods=10).min()
    
    df["distance_from_rolling_high"] = (close / (rolling_20_high + epsilon)) - 1  # Sẽ <= 0. Càng gần 0 nghĩa là giá đang áp sát đỉnh 20 phiên.
    df["distance_from_rolling_low"] = (close / (rolling_20_low + epsilon)) - 1    # Sẽ >= 0. Càng gần 0 nghĩa là giá đang áp sát đáy 20 phiên.

    return df
