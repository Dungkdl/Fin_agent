"""Định nghĩa khuôn mẫu (Base Class) cho tất cả các mô hình Quant."""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseQuantModel(ABC):
    """
    Interface bắt buộc đối với bất kỳ mô hình dự đoán nào được thêm vào hệ thống.
    """
    def __init__(self, config: dict):
        self.config = config
        self.model = None
        self.calibrator = None
        
    @abstractmethod
    def train(self, df_train: pd.DataFrame, cv_splitter=None) -> None:
        """
        Huấn luyện mô hình.
        Nếu truyền cv_splitter, mô hình có thể tự chạy Hyperparameter Tuning (ví dụ: Optuna).
        """
        pass

    @abstractmethod
    def predict_proba(self, df_test: pd.DataFrame) -> np.ndarray:
        """
        Dự đoán xác suất cho các nhãn (Bullish, Sideways, Bearish).
        """
        pass
        
    @abstractmethod
    def predict(self, df_test: pd.DataFrame) -> np.ndarray:
        """
        Dự đoán nhãn chính thức.
        """
        pass

    @abstractmethod
    def save(self, model_dir: str) -> None:
        """
        Lưu trạng thái mô hình ra đĩa (joblib, pickle, txt...).
        """
        pass

    @classmethod
    @abstractmethod
    def load(cls, model_dir: str, config: dict) -> "BaseQuantModel":
        """
        Khôi phục mô hình từ đĩa.
        """
        pass
