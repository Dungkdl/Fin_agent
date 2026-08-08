"""Tính toán các đặc trưng về thanh khoản và giao dịch (Volume & Trade Activity)."""

import pandas as pd
import numpy as np


def add_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    base_vol = df["base_volume"]
    quote_vol = df["quote_volume"]
    trades = df["trade_count"]
    
    epsilon = 1e-8
    
    # Volume changes
    df["base_volume_change"] = (base_vol / (base_vol.shift(1) + epsilon)) - 1
    df["quote_volume_change"] = (quote_vol / (quote_vol.shift(1) + epsilon)) - 1
    df["trade_count_change"] = (trades / (trades.shift(1) + epsilon)) - 1
    
    # Ratios against 20-period moving average
    quote_vol_ma20 = quote_vol.rolling(window=20, min_periods=10).mean()
    trades_ma20 = trades.rolling(window=20, min_periods=10).mean()
    
    df["quote_volume_ratio_20"] = quote_vol / (quote_vol_ma20 + epsilon)
    df["trade_count_ratio_20"] = trades / (trades_ma20 + epsilon)
    
    # Trade characteristics
    df["average_trade_size"] = base_vol / np.maximum(trades, epsilon)
    
    # Taker behavior
    taker_base = df["taker_buy_base_volume"]
    taker_quote = df["taker_buy_quote_volume"]
    
    df["taker_buy_base_ratio"] = taker_base / np.maximum(base_vol, epsilon)
    df["taker_buy_quote_ratio"] = taker_quote / np.maximum(quote_vol, epsilon)
    
    # Correlation between price return and volume
    price_return = df["close"].pct_change()
    df["volume_price_correlation"] = price_return.rolling(window=20, min_periods=10).corr(base_vol)
    
    return df
