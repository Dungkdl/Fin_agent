"""Kiểm định và làm sạch Features trước khi đưa vào Model."""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def validate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Kiểm tra DataFrame chứa features.
    Thay thế các giá trị vô cực (inf, -inf) sinh ra do chia cho số 0 bằng NaN.
    Cắt bớt các giá trị cực biên (Clip outliers) nếu cần thiết.
    """
    df = df.copy()
    
    # 1. Phát hiện và xử lý vô cực
    # Pandas mặc định coi inf là float, nhưng LightGBM sẽ báo lỗi nếu gặp inf.
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # 2. Log cảnh báo nếu có quá nhiều NaN (Chỉ log, không drop ở bước này vì LightGBM handle được NaN)
    nan_counts = df.isna().sum()
    high_nan_cols = nan_counts[nan_counts > len(df) * 0.5]
    if not high_nan_cols.empty:
        logger.warning(f"Cảnh báo: Các cột sau có hơn 50% giá trị NaN:\\n{high_nan_cols}")
        
    return df
