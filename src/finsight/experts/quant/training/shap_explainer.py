"""Sử dụng SHAP để diễn giải mô hình."""

import shap
import pandas as pd
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def explain_model_with_shap(model, df_test: pd.DataFrame, features: list, model_dir: Path):
    """
    Sử dụng SHAP TreeExplainer để phân tích tầm quan trọng của Features.
    - model: Đối tượng mô hình gốc (vd: lgb.Booster, xgb.XGBClassifier, catboost.CatBoostClassifier)
    - df_test: Tập dữ liệu holdout
    - features: Danh sách các cột đặc trưng dùng để dự đoán
    """
    try:
        X = df_test[features].copy()
        
        # Một số mô hình (như LightGBM) cần categorical là 'category' dtype
        for col in X.columns:
            if X[col].dtype == "object":
                X[col] = X[col].astype("category")
                
        # Giới hạn số lượng mẫu để giải thích cho nhanh (vd: max 1000)
        if len(X) > 1000:
            X_sample = X.sample(1000, random_state=42)
        else:
            X_sample = X
            
        logger.info(f"Tính toán SHAP values trên {len(X_sample)} samples...")
        
        if hasattr(model, "named_steps") or "Pipeline" in str(type(model)):
            logger.info("Bỏ qua SHAP Explainer vì mô hình là dạng Pipeline/Linear (không hỗ trợ TreeExplainer).")
            return []
            
        if "catboost" in str(type(model)).lower():
            logger.info("Bỏ qua SHAP Explainer cho CatBoost để tránh lỗi silent crash (segmentation fault) trên thư viện SHAP hiện tại.")
            return []

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
        
        # shap_values thường là list các mảng cho multi-class (1 array cho mỗi class)
        # Ta có 3 classes: BEARISH (0), SIDEWAYS (1), BULLISH (2). Ta quan tâm nhất đến BULLISH
        if isinstance(shap_values, list) and len(shap_values) > 2:
            shap_values_bullish = shap_values[2]
        else:
            # Tùy version SHAP hoặc thuật toán, đôi khi nó trả về array 3D (samples, features, classes)
            if isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
                shap_values_bullish = shap_values[:, :, 2]
            else:
                shap_values_bullish = shap_values
                
        # Tính Feature Importance trung bình tuyệt đối
        mean_abs_shap = np.abs(shap_values_bullish).mean(axis=0)
        
        importance_df = pd.DataFrame({
            "feature": features,
            "shap_importance": mean_abs_shap
        }).sort_values(by="shap_importance", ascending=False)
        
        # Lưu ra JSON
        output_file = model_dir / "shap_importance.json"
        importance_df.to_json(output_file, orient="records")
        logger.info(f"Lưu SHAP feature importance tại {output_file}")
        
        return importance_df.to_dict(orient="records")
        
    except Exception as e:
        logger.warning(f"Bỏ qua SHAP Explainer do lỗi không tương thích: {e}")
        return []
