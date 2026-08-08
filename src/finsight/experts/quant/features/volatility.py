"""Tính toán các chỉ báo độ biến động (Volatility)."""

import pandas as pd
import numpy as np

def add_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]
    
    # Đảm bảo đã có log_return_1, nếu chưa thì tính tạm
    log_return = np.log(close / close.shift(1))
    
    # Rolling volatility
    for window in [4, 16, 48]:
        df[f"rolling_volatility_{window}"] = log_return.rolling(window=window, min_periods=window//2).std()
        
    # ATR_14 (Average True Range)
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR_14"] = tr.ewm(span=14, adjust=False, min_periods=7).mean()
    
    # Bollinger Bandwidth
    sma_20 = close.rolling(window=20, min_periods=10).mean()
    std_20 = close.rolling(window=20, min_periods=10).std()
    epsilon = 1e-8
    df["bollinger_bandwidth"] = (4 * std_20) / (sma_20 + epsilon)
    
    # Rolling return skewness and kurtosis (window 20)
    df["rolling_return_skew"] = log_return.rolling(window=20, min_periods=10).skew()
    df["rolling_return_kurtosis"] = log_return.rolling(window=20, min_periods=10).kurt()
    
    return df
