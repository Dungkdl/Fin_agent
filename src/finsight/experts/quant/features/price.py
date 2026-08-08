"""Tính toán các chỉ số về giá."""

import numpy as np
import pandas as pd


def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]
    open_p = df["open"]

    # Returns
    for period in [1, 2, 4, 8, 16]:
        df[f"return_{period}"] = close.pct_change(periods=period)

    # Log return
    df["log_return_1"] = np.log(close / close.shift(1))

    # Ranges
    epsilon = 1e-8
    df["high_low_range"] = (high - low) / (close + epsilon)
    df["close_open_range"] = (close - open_p) / (open_p + epsilon)
    df["close_position_in_range"] = (close - low) / (high - low + epsilon)

    # Rolling distance
    rolling_20_high = high.rolling(window=20, min_periods=10).max()
    rolling_20_low = low.rolling(window=20, min_periods=10).min()
    
    df["distance_from_rolling_high"] = (close / (rolling_20_high + epsilon)) - 1
    df["distance_from_rolling_low"] = (close / (rolling_20_low + epsilon)) - 1

    return df
