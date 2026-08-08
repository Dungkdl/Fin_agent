"""Unit tests cho các tính năng của Quant."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from finsight.experts.quant.feature_engineering.features.price import add_price_features
from finsight.experts.quant.feature_engineering.features.volatility import add_volatility_features
from finsight.experts.quant.feature_engineering.features.momentum import add_momentum_features
from finsight.experts.quant.feature_engineering.features.volume import add_volume_features
from finsight.experts.quant.feature_engineering.features.time_features import add_time_features
from finsight.experts.quant.feature_engineering.features.validation import validate_features

def create_mock_candles(periods=100) -> pd.DataFrame:
    base_time = datetime(2023, 1, 1)
    
    times = [base_time + timedelta(minutes=15 * i) for i in range(periods)]
    
    # Fake OHLCV
    np.random.seed(42)
    closes = 20000 + np.random.randn(periods).cumsum() * 100
    highs = closes + np.random.rand(periods) * 50
    lows = closes - np.random.rand(periods) * 50
    opens = closes.copy()
    opens[1:] = closes[:-1] # Open is previous close
    
    volumes = np.random.rand(periods) * 10
    
    df = pd.DataFrame({
        "open_time": times,
        "close_time": times,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "base_volume": volumes,
        "quote_volume": volumes * closes,
        "trade_count": np.random.randint(100, 1000, periods),
        "taker_buy_base_volume": volumes * 0.4,
        "taker_buy_quote_volume": volumes * closes * 0.4
    })
    
    return df

def test_features_generation_and_validation():
    df = create_mock_candles()
    
    # Test Price
    df = add_price_features(df)
    assert "return_1" in df.columns
    assert "distance_from_rolling_high" in df.columns
    
    # Test Volatility
    df = add_volatility_features(df)
    assert "ATR_14_pct" in df.columns
    
    # Test Momentum
    df = add_momentum_features(df)
    assert "MACD_normalized" in df.columns
    
    # Test Volume
    df = add_volume_features(df)
    assert "volume_price_correlation" in df.columns
    
    # Test Time
    df = add_time_features(df)
    assert "hour_sin" in df.columns
    
    # Introduce an artificial inf
    df.loc[df.index[-1], "return_1"] = np.inf
    
    # Validate
    df_clean = validate_features(df)
    
    # Ensure inf is replaced by nan
    assert not np.isinf(df_clean["return_1"]).any()
    
    # Ensure dropna works (removes initial rolling NaNs and the last row with NaN return)
    df_final = df_clean.dropna()
    assert len(df_final) > 0
    assert len(df_final) < len(df)
