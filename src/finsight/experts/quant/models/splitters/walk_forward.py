"""Triển khai chiến lược Walk-Forward Cross Validation (Expanding Window)."""

import pandas as pd
import numpy as np

class WalkForwardSplitter:
    """
    Chia dữ liệu theo phương pháp Expanding Window.
    Bảo vệ chống rò rỉ dữ liệu (Data Leakage) bằng cơ chế Embargo.
    """
    def __init__(
        self, 
        min_train_months: int = 12, 
        validation_months: int = 3, 
        step_months: int = 3,
        embargo_steps: int = 5
    ):
        self.min_train_months = min_train_months
        self.validation_months = validation_months
        self.step_months = step_months
        self.embargo_steps = embargo_steps

    def split(self, df: pd.DataFrame, time_col: str = "close_time"):
        """
        Yields (train_idx, val_idx)
        """
        df = df.sort_values(time_col).reset_index(drop=True)
        times = df[time_col]
        
        start_time = times.min()
        end_time = times.max()
        
        # Điểm bắt đầu của Validation Set đầu tiên
        current_val_start = start_time + pd.DateOffset(months=self.min_train_months)
        
        while current_val_start < end_time:
            current_val_end = current_val_start + pd.DateOffset(months=self.validation_months)
            if current_val_end > end_time:
                current_val_end = end_time
                
            # Tập Validation
            val_mask = (times >= current_val_start) & (times < current_val_end)
            val_idx = df.index[val_mask].to_numpy()
            
            if len(val_idx) == 0:
                break
                
            # Đảm bảo Embargo (khoảng cách an toàn)
            # Tập Train kết thúc trước khi Validation bắt đầu một khoảng bằng embargo_steps (forecast horizon)
            # Tính bằng số lượng nến (steps) hoặc quy đổi ra thời gian thực tế nếu biết interval.
            # Để đơn giản, ta tìm index của nến sát trước current_val_start, rồi lùi lại embargo_steps
            first_val_idx = val_idx[0]
            train_end_idx = first_val_idx - self.embargo_steps
            
            if train_end_idx <= 0:
                # Nếu không đủ dữ liệu train
                current_val_start = current_val_start + pd.DateOffset(months=self.step_months)
                continue
                
            train_time_limit = times.iloc[train_end_idx - 1]
            train_mask = times <= train_time_limit
            train_idx = df.index[train_mask].to_numpy()
            
            if len(train_idx) > 0:
                yield train_idx, val_idx
                
            current_val_start = current_val_start + pd.DateOffset(months=self.step_months)
