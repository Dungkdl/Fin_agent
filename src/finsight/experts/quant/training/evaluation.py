"""Module tính toán các chỉ số đánh giá mô hình phân loại (Classification Metrics)."""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    f1_score, 
    balanced_accuracy_score, 
    precision_score, 
    recall_score, 
    confusion_matrix, 
    log_loss, 
    brier_score_loss
)

def evaluate_classification(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> dict:
    """
    Tính toán các chỉ số classification theo yêu cầu của hệ thống Quant.
    Ghi chú: y_true và y_pred là các label số nguyên (0: BEARISH, 1: SIDEWAYS, 2: BULLISH).
    y_prob là ma trận xác suất (N, 3).
    """
    labels = [0, 1, 2]
    
    # 1. Global Metrics
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    bal_acc = balanced_accuracy_score(y_true, y_pred)
    loss = log_loss(y_true, y_prob, labels=labels)
    
    # 2. Per-class Metrics
    precisions = precision_score(y_true, y_pred, average=None, labels=labels, zero_division=0)
    recalls = recall_score(y_true, y_pred, average=None, labels=labels, zero_division=0)
    
    class_names = ["BEARISH", "SIDEWAYS", "BULLISH"]
    per_class_precision = {c: float(p) for c, p in zip(class_names, precisions)}
    per_class_recall = {c: float(r) for c, r in zip(class_names, recalls)}
    
    # 3. Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    
    # 4. Brier score (multi-class approximated by one-vs-rest average)
    brier_scores = []
    for i in range(3):
        y_true_binary = (y_true == i).astype(int)
        brier = brier_score_loss(y_true_binary, y_prob[:, i])
        brier_scores.append(brier)
    avg_brier = float(np.mean(brier_scores))
    
    return {
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "balanced_accuracy": float(bal_acc),
        "log_loss": float(loss),
        "brier_score": avg_brier,
        "per_class_precision": per_class_precision,
        "per_class_recall": per_class_recall,
        "confusion_matrix": cm
    }

def evaluate_slices(df: pd.DataFrame, y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> dict:
    """
    Phân rã (slice) metrics theo symbol, regime
    df là DataFrame test gốc có chứa các cột siêu dữ liệu.
    """
    slices_metrics = {
        "by_symbol": {},
        "by_regime": {}
    }
    
    # Slice theo Symbol
    if "symbol" in df.columns:
        for sym in df["symbol"].unique():
            mask = df["symbol"] == sym
            if mask.sum() > 0:
                slices_metrics["by_symbol"][sym] = evaluate_classification(
                    y_true[mask], y_pred[mask], y_prob[mask]
                )
                
    # Slice theo Regime
    if "market_regime" in df.columns:
        for reg in df["market_regime"].unique():
            mask = df["market_regime"] == reg
            if mask.sum() > 0:
                slices_metrics["by_regime"][str(reg)] = evaluate_classification(
                    y_true[mask], y_pred[mask], y_prob[mask]
                )
                
    return slices_metrics
