"""Mô phỏng Giao dịch (Backtest) trên tập dữ liệu Holdout."""

import pandas as pd
import numpy as np

def run_spot_backtest(df: pd.DataFrame, config: dict) -> dict:
    """
    Giả lập giao dịch Spot (Spot-safe mode: Không short).
    Đã hỗ trợ Multi-symbol: Tách từng đồng coin ra backtest riêng rồi tính trung bình/tổng.
    """
    prob_threshold = config.get("probability_threshold", 0.55)
    fee_bps = config.get("fee_bps", 10) / 10000.0
    slippage_bps = config.get("slippage_bps", 5) / 10000.0
    
    if "symbol" not in df.columns:
        df["symbol"] = "UNKNOWN"
        
    all_trades = []
    final_equities = []
    max_drawdowns = []
    
    for sym, sdf in df.groupby("symbol", observed=True):
        sdf = sdf.sort_values("close_time").reset_index(drop=True)
        
        in_position = False
        entry_price = 0.0
        
        current_equity = 1.0
        equity_curve = [1.0]
        
        for i in range(len(sdf)):
            row = sdf.iloc[i]
            price = row["close"]
            p_bull = row.get("prob_BULLISH", 0)
            p_bear = row.get("prob_BEARISH", 0)
            
            if not in_position and p_bull >= prob_threshold:
                in_position = True
                entry_price = price * (1 + slippage_bps)
                current_equity *= (1 - fee_bps)
                
            elif in_position and p_bear >= prob_threshold:
                exit_price = price * (1 - slippage_bps)
                trade_return = (exit_price - entry_price) / entry_price
                current_equity *= (1 + trade_return)
                current_equity *= (1 - fee_bps)
                
                all_trades.append(trade_return)
                in_position = False
                
            equity_curve.append(current_equity)
            
        if in_position:
            final_price = sdf.iloc[-1]["close"] * (1 - slippage_bps)
            trade_return = (final_price - entry_price) / entry_price
            current_equity *= (1 + trade_return)
            current_equity *= (1 - fee_bps)
            all_trades.append(trade_return)
            
        final_equities.append(current_equity)
        
        eq_series = pd.Series(equity_curve)
        mdd = (eq_series - eq_series.cummax()) / eq_series.cummax()
        max_drawdowns.append(mdd.min())
        
    # Aggregate results across all symbols
    avg_net_return = np.mean([eq - 1.0 for eq in final_equities]) if final_equities else 0.0
    avg_max_drawdown = np.mean(max_drawdowns) if max_drawdowns else 0.0
    
    if len(all_trades) > 0:
        win_rate = sum([1 for r in all_trades if r > 0]) / len(all_trades)
        avg_trade = np.mean(all_trades)
        sharpe = (np.mean(all_trades) / np.std(all_trades) * np.sqrt(len(all_trades))) if np.std(all_trades) > 0 else 0.0
    else:
        win_rate = 0.0
        avg_trade = 0.0
        sharpe = 0.0

    return {
        "net_return": float(avg_net_return),
        "gross_return_estimate": float(avg_net_return),
        "max_drawdown": float(avg_max_drawdown),
        "win_rate": float(win_rate),
        "total_trades": len(all_trades),
        "average_trade_return": float(avg_trade),
        "pseudo_sharpe_ratio": float(sharpe),
        "final_equity": float(np.mean(final_equities)) if final_equities else 1.0
    }
