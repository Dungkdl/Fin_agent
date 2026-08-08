"""Tính toán các đặc trưng về thanh khoản và giao dịch (Volume & Trade Activity)."""

import pandas as pd
import numpy as np


def add_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    base_vol = df["base_volume"]
    quote_vol = df["quote_volume"]
    trades = df["trade_count"]
    
    epsilon = 1e-8
    
    # 1. Volume changes (Tốc độ thay đổi thanh khoản):
    # Ý nghĩa: Nếu base_volume_change tăng đột biến -> Báo hiệu có dòng tiền lớn (cá mập) vừa tham gia thị trường.
    df["base_volume_change"] = (base_vol / (base_vol.shift(1) + epsilon)) - 1
    df["quote_volume_change"] = (quote_vol / (quote_vol.shift(1) + epsilon)) - 1
    df["trade_count_change"] = (trades / (trades.shift(1) + epsilon)) - 1
    
    # 2. Ratios against 20-period moving average (Đột biến so với trung bình 20 phiên):
    # Ý nghĩa: Đánh giá xem khối lượng nến này là bình thường hay bùng nổ (Volume Breakout).
    quote_vol_ma20 = quote_vol.rolling(window=20, min_periods=10).mean()
    trades_ma20 = trades.rolling(window=20, min_periods=10).mean()
    
    df["quote_volume_ratio_20"] = quote_vol / (quote_vol_ma20 + epsilon)
    df["trade_count_ratio_20"] = trades / (trades_ma20 + epsilon)
    
    # 3. Trade characteristics (Quy mô lệnh trung bình):
    # Ý nghĩa: Nếu average_trade_size tự nhiên tăng vọt -> Ít lệnh nhưng lệnh nào cũng to -> Cá mập đang gom/xả hàng.
    df["average_trade_size"] = base_vol / np.maximum(trades, epsilon)
    
    # 4. Taker behavior (Hành vi Mua chủ động):
    # Ý nghĩa: Tỷ lệ Taker Buy > 0.5 nghĩa là phe Mua đang chủ động nuốt chửng các lệnh bán treo sẵn (Bullish). Ngược lại là Bearish.
    taker_base = df["taker_buy_base_volume"]
    taker_quote = df["taker_buy_quote_volume"]
    
    df["taker_buy_base_ratio"] = taker_base / np.maximum(base_vol, epsilon)
    df["taker_buy_quote_ratio"] = taker_quote / np.maximum(quote_vol, epsilon)
    
    # 5. Correlation between price return and volume (Tương quan giữa Giá và Khối lượng):
    # Ý nghĩa: Nếu Giá tăng + Volume tăng (corr > 0) -> Xu hướng tăng bền vững. Nếu Giá tăng + Volume giảm (corr < 0) -> Tăng ảo (Divergence).
    price_return = df["close"].pct_change()
    df["volume_price_correlation"] = price_return.rolling(window=20, min_periods=10).corr(base_vol)
    
    return df
