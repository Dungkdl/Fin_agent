"""Model registry để tự động khởi tạo đúng loại Model theo config."""

from finsight.experts.quant.models.lightgbm_model import LightGBMQuantModel
from finsight.experts.quant.models.xgboost_model import XGBoostQuantModel
from finsight.experts.quant.models.catboost_model import CatBoostQuantModel
from finsight.experts.quant.models.logistic_regression import LogisticRegressionQuantModel

MODEL_REGISTRY = {
    "lightgbm": LightGBMQuantModel,
    "xgboost": XGBoostQuantModel,
    "catboost": CatBoostQuantModel,
    "logistic_regression": LogisticRegressionQuantModel
}

def get_quant_model(config: dict):
    """
    Factory pattern để sinh ra Model class.
    Cấu hình trong YAML:
    model:
      type: "lightgbm" # hoặc "xgboost", "catboost"
    """
    model_type = config.get("type", "lightgbm")
    
    if model_type not in MODEL_REGISTRY:
        raise ValueError(f"Model type '{model_type}' không được hỗ trợ! Các loại hợp lệ: {list(MODEL_REGISTRY.keys())}")
        
    model_class = MODEL_REGISTRY[model_type]
    return model_class(config)
