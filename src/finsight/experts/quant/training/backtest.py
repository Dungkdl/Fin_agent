"""Mô phỏng Giao dịch (Backtest) trên tập dữ liệu Holdout."""

import pandas as pd
import numpy as np

def run_spot_backtest(df: pd.DataFrame, config: dict) -> dict:
    """
    Giả lập giao dịch Spot (Spot-safe mode: Không short).
    df: Cần chứa các cột ['close_time', 'close', 'future_return_t', 'prob_bullish', 'prob_bearish']
    hoặc tương đương. Giả sử ta backtest dựa trên giá 'close' hiện tại.
    """
    # Lấy configs
    prob_threshold = config.get("probability_threshold", 0.55)
    fee_bps = config.get("fee_bps", 10) / 10000.0
    slippage_bps = config.get("slippage_bps", 5) / 10000.0
    
    # Sort data by time
    df = df.sort_values("close_time").reset_index(drop=True)
    
    in_position = False
    entry_price = 0.0
    
    trades = []
    equity_curve = [1.0] # Bắt đầu với 1 đơn vị vốn
    current_equity = 1.0
    
    for i in range(len(df)):
        row = df.iloc[i]
        price = row["close"]
        p_bull = row.get("prob_BULLISH", 0)
        p_bear = row.get("prob_BEARISH", 0)
        
        # Tính toán giá trị danh mục nếu đang giữ vị thế
        if in_position:
            # Mark-to-market
            pass # Sẽ tính mượt hơn qua chuỗi return, nhưng ở đây tính trade-based
            
        # Logic tạo tín hiệu (Signal)
        if not in_position and p_bull >= prob_threshold:
            # Mua (Long)
            in_position = True
            # Thực tế mua sẽ bị slippage làm giá cao hơn và mất fee
            entry_price = price * (1 + slippage_bps)
            current_equity *= (1 - fee_bps) # Mất phí mua
            
        elif in_position and p_bear >= prob_threshold:
            # Bán (Exit)
            # Bán bị slippage làm giá thấp hơn và mất fee
            exit_price = price * (1 - slippage_bps)
            
            # Tính PnL của trade
            trade_return = (exit_price - entry_price) / entry_price
            current_equity *= (1 + trade_return)
            current_equity *= (1 - fee_bps) # Mất phí bán
            
            trades.append(trade_return)
            in_position = False
            
        equity_curve.append(current_equity)

    # Đóng vị thế cưỡng bức ở cuối kỳ nếu còn giữ
    if in_position:
        final_price = df.iloc[-1]["close"] * (1 - slippage_bps)
        trade_return = (final_price - entry_price) / entry_price
        current_equity *= (1 + trade_return)
        current_equity *= (1 - fee_bps)
        trades.append(trade_return)
        
    equity_series = pd.Series(equity_curve)
    
    # 1. Gross & Net Return
    net_return = current_equity - 1.0
    # Gross return ước tính (bỏ qua fee và slippage)
    gross_return = net_return # Simplification, to be fully accurate we'd simulate without fee/slippage
    
    # 2. Maximum Drawdown
    rolling_max = equity_series.cummax()
    drawdowns = (equity_series - rolling_max) / rolling_max
    max_drawdown = drawdowns.min()
    
    # 3. Win Rate & Trade Stats
    if len(trades) > 0:
        win_rate = sum([1 for r in trades if r > 0]) / len(trades)
        avg_trade = np.mean(trades)
    else:
        win_rate = 0.0
        avg_trade = 0.0
        
    # 4. Sharpe Ratio (Giả sử 1 năm có 365 ngày giao dịch)
    # Vì equity curve tính theo event/candle, việc tính chuẩn Sharpe cần return theo ngày.
    # Tính Sharpe đơn giản qua trade returns (không chuẩn hoàn toàn nhưng đủ dùng làm baseline)
    if len(trades) > 1 and np.std(trades) > 0:
        sharpe_ratio = np.mean(trades) / np.std(trades) * np.sqrt(len(trades)) # annualized by number of trades
    else:
        sharpe_ratio = 0.0

    return {
        "net_return": float(net_return),
        "gross_return_estimate": float(gross_return),
        "max_drawdown": float(max_drawdown),
        "win_rate": float(win_rate),
        "total_trades": len(trades),
        "average_trade_return": float(avg_trade),
        "pseudo_sharpe_ratio": float(sharpe_ratio),
        "final_equity": float(current_equity)
    }
