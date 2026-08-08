"""Tính toán Regime weight (Tăng trọng số cho sample cùng trạng thái thị trường)."""

import pandas as pd


def compute_regime_weight(df: pd.DataFrame, target_regime: str = None) -> pd.Series:
    """
    target_regime: Trạng thái thị trường hiện tại (lúc inference/test).
    Nếu sample trong training set có cùng regime với target_regime, tăng trọng số.
    """
    if len(df) == 0 or "market_regime" not in df.columns:
        return pd.Series(1.0, index=df.index)
        
    weight = pd.Series(1.0, index=df.index)
    
    if target_regime is not None:
        # Tăng gấp đôi trọng số cho các nến có cùng trạng thái thị trường
        is_same_regime = (df["market_regime"] == target_regime)
        weight.loc[is_same_regime] = 2.0
        
    return weight
