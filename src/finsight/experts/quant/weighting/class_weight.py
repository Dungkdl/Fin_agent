"""Tính toán Class weight để cân bằng dữ liệu."""

import pandas as pd


def compute_class_weight(df: pd.DataFrame, label_col: str = "direction_label") -> pd.Series:
    """
    Tính trọng số để cân bằng các class (BULLISH, BEARISH, SIDEWAYS).
    Công thức phổ biến: weight = total_samples / (num_classes * class_count)
    """
    if len(df) == 0 or label_col not in df.columns:
        return pd.Series(1.0, index=df.index)
        
    class_counts = df[label_col].value_counts()
    total_samples = len(df)
    num_classes = len(class_counts)
    
    # Tạo dictionary map từ label sang weight
    weight_map = {
        label: total_samples / (num_classes * count)
        for label, count in class_counts.items()
    }
    
    return df[label_col].map(weight_map).fillna(1.0)
