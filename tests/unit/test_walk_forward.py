import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from finsight.experts.quant.models.splitters.walk_forward import WalkForwardSplitter

def create_dummy_timeseries(months=24, interval_hours=24):
    start = datetime(2023, 1, 1)
    end = start + pd.DateOffset(months=months)
    times = pd.date_range(start=start, end=end, freq=f'{interval_hours}h')
    df = pd.DataFrame({"close_time": times, "value": np.arange(len(times))})
    return df

def test_walk_forward_splitter_no_leakage():
    df = create_dummy_timeseries(months=24, interval_hours=24) # 1 nến = 1 ngày
    
    embargo_steps = 5
    splitter = WalkForwardSplitter(
        min_train_months=6,
        validation_months=2,
        step_months=2,
        embargo_steps=embargo_steps
    )
    
    splits = list(splitter.split(df, time_col="close_time"))
    
    assert len(splits) > 0
    
    for train_idx, val_idx in splits:
        train_times = df.loc[train_idx, "close_time"]
        val_times = df.loc[val_idx, "close_time"]
        
        max_train_time = train_times.max()
        min_val_time = val_times.min()
        
        # Check no overlap
        assert max_train_time < min_val_time
        
        # Check embargo strictly
        # Khoảng cách giữa nến cuối cùng của train và nến đầu tiên của val 
        # phải ÍT NHẤT bằng embargo_steps + 1 nến
        # Vì nếu embargo=5, nến cuối train là i-5, thì khoảng cách index là 5.
        train_end_idx = train_idx[-1]
        val_start_idx = val_idx[0]
        
        assert (val_start_idx - train_end_idx) >= embargo_steps
        
        print(f"Train end: {max_train_time}, Val start: {min_val_time}, Gap steps: {val_start_idx - train_end_idx}")
