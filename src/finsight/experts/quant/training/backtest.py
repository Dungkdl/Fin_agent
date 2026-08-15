"""Mô phỏng Giao dịch (Backtest) trên tập dữ liệu Holdout."""

import pandas as pd
import numpy as np

def run_spot_backtest(df: pd.DataFrame, config: dict) -> dict:
    """
    Giả lập giao dịch Spot (Spot-safe mode: Không short).
    - Signal T -> Execute Open T+1 (Chống Look-ahead bias)
    - Fixed 5-day Horizon Exit (Đồng bộ với model target)
    - Có Baseline Equal Weight
    """
    prob_threshold = config.get("probability_threshold", 0.55)
    fee_bps = config.get("fee_bps", 10) / 10000.0
    slippage_bps = config.get("slippage_bps", 5) / 10000.0
    forecast_steps = config.get("forecast_steps", 5)
    
    if "symbol" not in df.columns:
        df["symbol"] = "UNKNOWN"
        
    all_trades = []
    
    # Portfolio tracking
    # Ta sẽ build một timeline chung cho portfolio. 
    # Nhưng vì là event-driven backtest đơn giản, ta tính PnL từng trade rồi aggregate.
    
    final_equities = []
    max_drawdowns = []
    baseline_returns = []
    
    for sym, sdf in df.groupby("symbol", observed=True):
        sdf = sdf.sort_values("close_time").reset_index(drop=True)
        
        # Baseline: Mua ở cây nến đầu tiên, bán ở cây nến cuối cùng
        if len(sdf) > 0:
            bl_entry = sdf.iloc[0]["close"]
            bl_exit = sdf.iloc[-1]["close"]
            baseline_returns.append((bl_exit - bl_entry) / bl_entry)
            
        in_position = False
        entry_price = 0.0
        entry_idx = 0
        
        current_equity = 1.0
        equity_curve = [1.0]
        
        for i in range(len(sdf) - 1): # Trừ 1 để luôn có T+1
            row = sdf.iloc[i]
            p_bull = row.get("prob_BULLISH", 0)
            
            # Nếu đang có lệnh, kiểm tra xem đã đủ số nến chưa (Fixed Horizon)
            if in_position:
                if i - entry_idx >= forecast_steps:
                    # Tới hạn -> Bán ở Close của ngày thứ 5
                    exit_price = row["close"] * (1 - slippage_bps)
                    trade_return = (exit_price - entry_price) / entry_price
                    current_equity *= (1 + trade_return)
                    current_equity *= (1 - fee_bps)
                    
                    all_trades.append(trade_return)
                    in_position = False
            
            # Nếu chưa có lệnh, kiểm tra Signal
            if not in_position and p_bull >= prob_threshold:
                # Đặt lệnh Mua (Signal T) -> Khớp ở Open T+1
                in_position = True
                entry_idx = i
                # Nếu không có cột open, dùng close của T+1
                next_price = sdf.iloc[i+1]["open"] if "open" in sdf.columns else sdf.iloc[i+1]["close"]
                entry_price = next_price * (1 + slippage_bps)
                current_equity *= (1 - fee_bps)
                
            equity_curve.append(current_equity)
            
        # Cuối kỳ nếu còn giữ lệnh thì đóng cưỡng bức
        if in_position:
            final_price = sdf.iloc[-1]["close"] * (1 - slippage_bps)
            trade_return = (final_price - entry_price) / entry_price
            current_equity *= (1 + trade_return)
            current_equity *= (1 - fee_bps)
            all_trades.append(trade_return)
            equity_curve.append(current_equity)
            
        final_equities.append(current_equity)
        
        eq_series = pd.Series(equity_curve)
        if len(eq_series) > 0:
            mdd = (eq_series - eq_series.cummax()) / eq_series.cummax()
            max_drawdowns.append(mdd.min())
            
    # Aggregate results
    avg_net_return = np.mean([eq - 1.0 for eq in final_equities]) if final_equities else 0.0
    avg_max_drawdown = np.mean(max_drawdowns) if max_drawdowns else 0.0
    avg_baseline = np.mean(baseline_returns) if baseline_returns else 0.0
    
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
        "baseline_return": float(avg_baseline),
        "max_drawdown": float(avg_max_drawdown),
        "win_rate": float(win_rate),
        "total_trades": len(all_trades),
        "average_trade_return": float(avg_trade),
        "pseudo_sharpe_ratio": float(sharpe),
        "final_equity": float(np.mean(final_equities)) if final_equities else 1.0
    }
