"""Tính toán Market Regime (Trạng thái thị trường)."""

import pandas as pd
import numpy as np


def add_regime_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Xác định market regime dựa vào Trend (bullish, bearish, neutral) 
    và Volatility (high_vol, low_vol).
    """
    df = df.copy()
    close = df["close"]
    
    # Tính Trend state
    ema_20 = close.ewm(span=20, adjust=False, min_periods=10).mean()
    ema_50 = close.ewm(span=50, adjust=False, min_periods=25).mean()
    
    is_bullish = (close > ema_20) & (ema_20 > ema_50)
    is_bearish = (close < ema_20) & (ema_20 < ema_50)
    
    trend_state = pd.Series("neutral", index=df.index)
    trend_state.loc[is_bullish] = "bullish"
    trend_state.loc[is_bearish] = "bearish"
    
    # Tính Volatility state
    # Dùng ATR_14 (nếu chưa có thì tính tạm ở đây)
    high = df["high"]
    low = df["low"]
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr_14 = tr.ewm(span=14, adjust=False, min_periods=7).mean()
    
    # So sánh ATR hiện tại với ATR trung bình của 100 nến quá khứ (Rolling distribution)
    # Không dùng look-ahead data
    historical_atr_mean = atr_14.rolling(window=100, min_periods=20).mean()
    
    vol_state = pd.Series("low_vol", index=df.index)
    vol_state.loc[atr_14 > historical_atr_mean] = "high_vol"
    
    # Kết hợp
    # Ví dụ: "bullish" + "_" + "high_vol" -> "bullish_high_vol"
    df["market_regime"] = trend_state + "_" + vol_state
    
    # Vì output yêu cầu các trạng thái: bull_low_vol, bull_high_vol, bear_low_vol, bear_high_vol, neutral_low_vol, neutral_high_vol
    # Sửa từ "bullish" -> "bull" và "bearish" -> "bear" cho ngắn gọn
    df["market_regime"] = df["market_regime"].str.replace("bullish_", "bull_")
    df["market_regime"] = df["market_regime"].str.replace("bearish_", "bear_")
    
    return df
