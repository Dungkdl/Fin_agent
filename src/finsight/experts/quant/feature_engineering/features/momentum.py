"""Tính toán các chỉ báo động lượng (Momentum).Xem xu hướng giá đang có "động lượng" hay không"""

import pandas as pd
import numpy as np


def add_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]
    
    # 1. RSI_14 (Relative Strength Index):
    # Ý nghĩa: Chỉ báo dao động (từ 0-100) đo lường tốc độ và sự thay đổi của giá. RSI > 70 thường được coi là Quá mua (Overbought), RSI < 30 là Quá bán (Oversold).
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False, min_periods=7).mean()
    ema_down = down.ewm(com=13, adjust=False, min_periods=7).mean()
    rs = ema_up / (ema_down + 1e-8)
    df["RSI_14"] = 100 - (100 / (1 + rs))
    
    # 2. EMAs and MACD (Moving Average Convergence Divergence) Normalized:
    # Ý nghĩa MACD: Hiệu số giữa EMA nhanh (12) và EMA chậm (26). 
    # Phải chia cho giá Đóng cửa để chuẩn hóa biên độ, giúp AI không bị overfit bởi mệnh giá coin.
    ema_12 = close.ewm(span=12, adjust=False, min_periods=6).mean()
    ema_26 = close.ewm(span=26, adjust=False, min_periods=13).mean()
    
    df["EMA_12"] = ema_12
    df["EMA_26"] = ema_26
    df["EMA_ratio"] = ema_12 / (ema_26 + 1e-8)  # Tỷ lệ EMA nhanh / chậm. Nếu > 1 nghĩa là trend đang tăng.
    
    macd_raw = ema_12 - ema_26
    macd_signal_raw = macd_raw.ewm(span=9, adjust=False, min_periods=4).mean()
    
    df["MACD_normalized"] = macd_raw / close
    df["MACD_signal_normalized"] = macd_signal_raw / close
    df["MACD_histogram_normalized"] = (macd_raw - macd_signal_raw) / close  # Phân kỳ MACD chuẩn hóa
    
    # 3. Rate of Change (14 periods):
    # Ý nghĩa: Tốc độ thay đổi của giá so với 14 nến trước. Giá trị > 0 tức là giá đang tăng tốc lên trên.
    df["Rate_of_Change_14"] = (close / (close.shift(14) + 1e-8)) - 1
    
    # 4. Stochastic Oscillator (14 periods):
    # Ý nghĩa: Đo lường mức đóng cửa hiện tại so với khoảng đỉnh/đáy trong 14 nến qua (từ 0-100). 
    # Càng gần 100 nghĩa là giá liên tục đóng cửa ở mức cao nhất, thể hiện đà tăng bạo liệt.
    low_14 = low.rolling(window=14, min_periods=7).min()
    high_14 = high.rolling(window=14, min_periods=7).max()
    df["Stochastic_oscillator"] = (close - low_14) / (high_14 - low_14 + 1e-8) * 100
    
    return df
