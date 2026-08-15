"""Mô phỏng Giao dịch (Backtest) trên tập dữ liệu Holdout."""

import pandas as pd
import numpy as np

def run_spot_backtest(df: pd.DataFrame, config: dict) -> dict:
    """
    Giả lập giao dịch Spot Portfolio Mark-To-Market.
    - Signal T -> Khớp lệnh giá Open ngày T+1
    - Đánh giá Equity (Cash + Position Value) từng ngày.
    - Sharpe Ratio & MDD tính trên đường cong Equity hàng ngày.
    """
    prob_threshold = config.get("probability_threshold", 0.55)
    fee_bps = config.get("fee_bps", 10) / 10000.0
    slippage_bps = config.get("slippage_bps", 5) / 10000.0
    forecast_steps = config.get("forecast_steps", 5)
    
    if "symbol" not in df.columns:
        df["symbol"] = "UNKNOWN"
        
    df = df.sort_values("close_time").reset_index(drop=True)
    unique_times = df["close_time"].unique()
    
    cash = 1.0
    positions = {} # sym: {amount, entry_price, days_held}
    
    equity_curve = []
    baseline_curve = []
    
    # Baseline Buy & Hold Equal Weight
    baseline_cash = 1.0
    baseline_positions = {}
    day1_df = df[df["close_time"] == unique_times[0]]
    if not day1_df.empty:
        alloc_per_sym = baseline_cash / len(day1_df)
        for _, row in day1_df.iterrows():
            sym = row["symbol"]
            baseline_positions[sym] = alloc_per_sym / row["close"]
        baseline_cash = 0.0
    
    all_trades = []
    
    for t_idx, current_time in enumerate(unique_times):
        day_data = df[df["close_time"] == current_time]
        close_prices = dict(zip(day_data["symbol"], day_data["close"]))
        
        # 1. Update MTM Equity
        portfolio_value = cash
        baseline_value = baseline_cash
        
        for sym, pos in list(positions.items()):
            if sym in close_prices:
                current_price = close_prices[sym]
                portfolio_value += pos["amount"] * current_price
                pos["days_held"] += 1
                
                # Bán nếu đủ số nến Horizon
                if pos["days_held"] >= forecast_steps:
                    exit_price = current_price * (1 - slippage_bps)
                    revenue = pos["amount"] * exit_price * (1 - fee_bps)
                    
                    # Lưu log trade
                    trade_return = (exit_price - pos["entry_price"]) / pos["entry_price"]
                    all_trades.append(trade_return)
                    
                    cash += revenue
                    # Vì bán ngay lúc Close, phần tiền thu về sẽ thay thế cho giá trị cổ phiếu trong danh mục
                    portfolio_value = portfolio_value - (pos["amount"] * current_price) + revenue
                    del positions[sym]
                    
        for sym, amount in baseline_positions.items():
            if sym in close_prices:
                baseline_value += amount * close_prices[sym]
                
        equity_curve.append(portfolio_value)
        baseline_curve.append(baseline_value)
        
        # 2. Xử lý Signal và mua (Khớp lệnh T+1)
        bullish_signals = day_data[day_data["prob_BULLISH"] >= prob_threshold]
        symbols_to_buy = [sym for sym in bullish_signals["symbol"] if sym not in positions]
        
        if symbols_to_buy and cash > 0:
            alloc_per_sym = cash / len(symbols_to_buy)
            for sym in symbols_to_buy:
                # Lấy giá Open ngày hôm sau
                sym_future = df[(df["symbol"] == sym) & (df["close_time"] > current_time)]
                if not sym_future.empty:
                    next_row = sym_future.iloc[0]
                    next_price = next_row["open"] if "open" in next_row else next_row["close"]
                    entry_price = next_price * (1 + slippage_bps)
                    
                    amount = alloc_per_sym / (entry_price * (1 + fee_bps))
                    cash -= alloc_per_sym
                    positions[sym] = {
                        "amount": amount,
                        "entry_price": entry_price,
                        "days_held": 0
                    }
                    
    # Force close các vị thế còn sót lại
    if len(unique_times) > 0:
        final_time = unique_times[-1]
        last_day_data = df[df["close_time"] == final_time]
        close_prices = dict(zip(last_day_data["symbol"], last_day_data["close"]))
        
        for sym, pos in list(positions.items()):
            if sym in close_prices:
                exit_price = close_prices[sym] * (1 - slippage_bps)
                revenue = pos["amount"] * exit_price * (1 - fee_bps)
                cash += revenue
                trade_return = (exit_price - pos["entry_price"]) / pos["entry_price"]
                all_trades.append(trade_return)
                del positions[sym]
                
    # 3. Tính toán Metrics (Trên MTM Curve)
    eq_series = pd.Series(equity_curve)
    bl_series = pd.Series(baseline_curve)
    
    daily_returns = eq_series.pct_change().dropna()
    bl_returns = bl_series.pct_change().dropna()
    
    net_return = eq_series.iloc[-1] - 1.0 if not eq_series.empty else 0.0
    baseline_return = bl_series.iloc[-1] - 1.0 if not bl_series.empty else 0.0
    
    mdd = (eq_series - eq_series.cummax()) / eq_series.cummax()
    max_drawdown = mdd.min() if not mdd.empty else 0.0
    
    annualization_factor = np.sqrt(365)
    
    if len(daily_returns) > 0 and daily_returns.std() > 0:
        sharpe = (daily_returns.mean() / daily_returns.std()) * annualization_factor
    else:
        sharpe = 0.0
        
    if len(all_trades) > 0:
        win_rate = sum([1 for r in all_trades if r > 0]) / len(all_trades)
        avg_trade = np.mean(all_trades)
    else:
        win_rate = 0.0
        avg_trade = 0.0

    return {
        "net_return": float(net_return),
        "baseline_return": float(baseline_return),
        "max_drawdown": float(max_drawdown),
        "win_rate": float(win_rate),
        "total_trades": len(all_trades),
        "average_trade_return": float(avg_trade),
        "pseudo_sharpe_ratio": float(sharpe), # Tên giữ cũ nhưng bản chất là True Sharpe (MTM)
        "final_equity": float(eq_series.iloc[-1]) if not eq_series.empty else 1.0
    }
