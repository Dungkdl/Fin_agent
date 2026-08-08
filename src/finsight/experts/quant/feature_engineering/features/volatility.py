"""Tính toán các chỉ báo độ biến động (Volatility).
 Hay thường gọi là "biến động" hay "dao động", 
 "Volatility" đo lường mức độ biến động, lên xuống của giá tài sản trong một khoảng thời gian cụ thể. 
 Nói một cách đơn giản, nó cho biết giá của tài sản đó có xu hướng thay đổi nhanh hay chậm, mạnh hay nhẹ."""

import pandas as pd
import numpy as np

def add_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]
    
    # Đảm bảo đã có log_return_1, nếu chưa thì tính tạm
    log_return = np.log(close / close.shift(1))
    
    # 1. Rolling Volatility (Độ biến động cuộn):
    # Ý nghĩa: Đo lường mức độ rủi ro/dao động của thị trường trong các khung N nến qua. Giá trị càng lớn nghĩa là giá dao động càng mạnh.
    for window in [4, 16, 48]:
        df[f"rolling_volatility_{window}"] = log_return.rolling(window=window, min_periods=window//2).std()
        
    # 2. ATR_14_pct (Average True Range Normalized):
    # Ý nghĩa: Chỉ báo kinh điển đo lường biên độ dao động trung bình thực tế của giá. Rất hay dùng để đặt Stoploss.
    # Phải chuẩn hóa chia cho Close để Model học được tính tương quan giữa các coin có giá trị chênh lệch lớn (Cross-asset).
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["ATR_14_pct"] = tr.ewm(span=14, adjust=False, min_periods=7).mean() / close
    
    # 3. Bollinger Bandwidth (Độ rộng dải Bollinger):
    # Ý nghĩa: Khi dải Bollinger thắt chặt (Bandwidth nhỏ) -> thị trường tích lũy chờ bùng nổ. Khi dải phình to -> thị trường đang có xu hướng mạnh.
    sma_20 = close.rolling(window=20, min_periods=10).mean()
    std_20 = close.rolling(window=20, min_periods=10).std()
    epsilon = 1e-8
    df["bollinger_bandwidth"] = (4 * std_20) / (sma_20 + epsilon)
    
    # 4. Rolling Return Skewness và Kurtosis:
    # Ý nghĩa Skewness (Độ lệch): Lớn hơn 0 có nghĩa các phiên tăng giá mạnh thường xuyên xảy ra hơn. Nhỏ hơn 0 là có nguy cơ cắm mỏ (flash crash).
    # Ý nghĩa Kurtosis (Độ nhọn): Đo lường khả năng xuất hiện thiên nga đen (outliers). Giá trị cao nghĩa là thị trường giật giật rất bất thường.
    df["rolling_return_skew"] = log_return.rolling(window=20, min_periods=10).skew()
    df["rolling_return_kurtosis"] = log_return.rolling(window=20, min_periods=10).kurt()
    
    return df
