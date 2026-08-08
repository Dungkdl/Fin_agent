"""Tính toán các chỉ báo động lượng (Momentum)."""

import pandas as pd
import numpy as np


def add_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]
    
    # RSI_14
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False, min_periods=7).mean()
    ema_down = down.ewm(com=13, adjust=False, min_periods=7).mean()
    rs = ema_up / (ema_down + 1e-8)
    df["RSI_14"] = 100 - (100 / (1 + rs))
    
    # EMAs and MACD
    ema_12 = close.ewm(span=12, adjust=False, min_periods=6).mean()
    ema_26 = close.ewm(span=26, adjust=False, min_periods=13).mean()
    
    df["EMA_12"] = ema_12
    df["EMA_26"] = ema_26
    df["EMA_ratio"] = ema_12 / (ema_26 + 1e-8)
    
    df["MACD"] = ema_12 - ema_26
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False, min_periods=4).mean()
    df["MACD_histogram"] = df["MACD"] - df["MACD_signal"]
    
    # Rate of Change (14 periods)
    df["Rate_of_Change_14"] = (close / (close.shift(14) + 1e-8)) - 1
    
    # Stochastic Oscillator (14 periods)
    low_14 = low.rolling(window=14, min_periods=7).min()
    high_14 = high.rolling(window=14, min_periods=7).max()
    df["Stochastic_oscillator"] = (close - low_14) / (high_14 - low_14 + 1e-8) * 100
    
    return df
