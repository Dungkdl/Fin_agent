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
        embargo_steps: int = 5,
        input_interval: str = "1d"
    ):
        self.min_train_months = min_train_months
        self.validation_months = validation_months
        self.step_months = step_months
        self.embargo_steps = embargo_steps
        self.input_interval = input_interval
        
        # Chuyển đổi input_interval thành Timedelta
        interval_str = self.input_interval.lower()
        if interval_str.endswith('d'):
            self.td = pd.Timedelta(days=int(interval_str[:-1]))
        elif interval_str.endswith('h'):
            self.td = pd.Timedelta(hours=int(interval_str[:-1]))
        elif interval_str.endswith('m'):
            self.td = pd.Timedelta(minutes=int(interval_str[:-1]))
        else:
            self.td = pd.Timedelta(days=1)
            
        self.embargo_time = self.td * self.embargo_steps

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
                
            # Đảm bảo Embargo (khoảng cách an toàn bằng thời gian)
            train_time_limit = current_val_start - self.embargo_time
            
            train_mask = times < train_time_limit
            train_idx = df.index[train_mask].to_numpy()
            
            if len(train_idx) > 0:
                yield train_idx, val_idx
                
            current_val_start = current_val_start + pd.DateOffset(months=self.step_months)
