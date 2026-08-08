"""Tính toán các đặc trưng tương quan chéo (Cross-asset context)."""

import pandas as pd
import numpy as np


def add_cross_asset_features(df: pd.DataFrame, context_dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    context_dfs: Dictionary chứa DataFrame của các coin khác (vd: "BTCUSDT", "ETHUSDT").
    Yêu cầu các DataFrame trong context_dfs đã được tính sẵn các feature cơ bản (như return_1).
    """
    df = df.copy()
    
    # Đảm bảo index là thời gian để dùng merge_asof hoặc join point-in-time
    # Ở đây giả định df có cột 'close_time' dùng để join
    df_sorted = df.sort_values("close_time")
    
    # Hàm phụ trợ để lấy data an toàn
    def get_context_series(symbol: str, col_name: str) -> pd.Series | None:
        if symbol not in context_dfs:
            return None
        ctx_df = context_dfs[symbol].sort_values("close_time")
        
        # Merge asof đảm bảo tuyệt đối không nhìn tương lai
        # Lấy giá trị của ctx_df.col_name tại thời điểm <= df.close_time
        # Thêm tolerance=12h để tránh Stale Context (nếu đồng coin bị mất thanh khoản quá 12h thì không gán nhầm dữ liệu cũ rích)
        merged = pd.merge_asof(
            df_sorted[["close_time"]],
            ctx_df[["close_time", col_name]],
            on="close_time",
            direction="backward",
            tolerance=pd.Timedelta(hours=12)
        )
        # Bắt buộc gán lại index của df_sorted để Pandas tự động map đúng dòng khi gán lại vào df gốc
        merged.index = df_sorted.index
        return merged[col_name]
    
    # 1. Bối cảnh từ Bitcoin (BTC Context):
    # Ý nghĩa: BTC là xương sống của thị trường Crypto. Việc so sánh (relative_return) giúp AI nhận biết đồng coin hiện tại đang "khỏe hơn" (Outperform) hay "yếu hơn" (Underperform) so với BTC.
    btc_ret1 = get_context_series("BTCUSDT", "return_1")
    btc_ret4 = get_context_series("BTCUSDT", "return_4")
    btc_vol = get_context_series("BTCUSDT", "rolling_volatility_4")
    
    if btc_ret1 is not None:
        df["btc_return_1"] = btc_ret1
        df["relative_return_vs_btc"] = df["return_1"] - btc_ret1
    if btc_ret4 is not None:
        df["btc_return_4"] = btc_ret4
    if btc_vol is not None:
        df["btc_volatility"] = btc_vol
        
    # 2. Bối cảnh từ Ethereum (ETH Context):
    # Ý nghĩa: ETH là đồng dẫn dắt nhóm Altcoin. Nếu Altcoin tăng mà ETH không tăng -> Dòng tiền đang chốt lời chuyển sang penny (Rủi ro rũ bỏ cao).
    eth_ret1 = get_context_series("ETHUSDT", "return_1")
    eth_ret4 = get_context_series("ETHUSDT", "return_4")
    
    if eth_ret1 is not None:
        df["eth_return_1"] = eth_ret1
        df["relative_return_vs_eth"] = df["return_1"] - eth_ret1
    if eth_ret4 is not None:
        df["eth_return_4"] = eth_ret4
        
    # 3. Market Breadth (Độ rộng thị trường chung):
    # Ý nghĩa: Nếu market_return_breadth > 0.5 (Tức là hơn 50% số coin tăng giá) -> Thị trường đang trong pha sóng bùng nổ diện rộng (Uptrend thực sự).
    if len(context_dfs) > 0:
        # Tập hợp return_1 của toàn bộ market tại mỗi timestamp
        market_returns = []
        for sym, ctx_df in context_dfs.items():
            ret = get_context_series(sym, "return_1")
            if ret is not None:
                market_returns.append(ret)
                
        if market_returns:
            market_returns_arr = np.array(market_returns) # shape: (num_coins, num_rows)
            
            median_val = np.nanmedian(market_returns_arr, axis=0)
            df["market_median_return"] = pd.Series(median_val, index=df_sorted.index)
            
            # breadth = tỷ lệ coin có return > 0
            breadth_val = np.nanmean(market_returns_arr > 0, axis=0)
            df["market_return_breadth"] = pd.Series(breadth_val, index=df_sorted.index)
    
    return df
