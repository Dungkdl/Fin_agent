"""Triển khai mô hình LightGBM cho Quant Trading."""

import lightgbm as lgb
import optuna
import pandas as pd
import numpy as np
import logging
from pathlib import Path

from finsight.experts.quant.models.interface import BaseQuantModel

logger = logging.getLogger(__name__)

class LightGBMQuantModel(BaseQuantModel):
    def __init__(self, config: dict):
        super().__init__(config)
        self.features = [] # Danh sách cột đặc trưng
        self.target = "direction_label"
        self.weight_col = "final_weight"
        
        # Mặc định tham số nếu không tuning
        self.params = {
            "objective": self.config.get("objective", "multiclass"),
            "num_class": 3,
            "metric": "multi_logloss",
            "boosting_type": "gbdt",
            "learning_rate": 0.05,
            "num_leaves": 31,
            "random_state": self.config.get("random_seed", 42),
            "verbose": -1,
        }

    def _extract_features(self, df: pd.DataFrame):
        # Tự động trích xuất các cột feature (loại trừ các cột metadata)
        exclude_cols = [
            "exchange", "symbol", "interval", "open_time", "close_time", 
            "source", "source_file", "quality_status", "quality_flags",
            "future_return", "normalized_return", "direction_label",
            "class_weight", "recency_weight", "regime_weight", "quality_weight", "final_weight"
        ]
        self.features = [c for c in df.columns if c not in exclude_cols]
        
    def _map_labels(self, labels: pd.Series) -> pd.Series:
        mapping = {"BEARISH": 0, "SIDEWAYS": 1, "BULLISH": 2}
        return labels.map(mapping)

    def train(self, df_train: pd.DataFrame, cv_splitter=None) -> None:
        # Ép kiểu các cột object (string) sang category để LightGBM hỗ trợ
        for col in df_train.columns:
            if df_train[col].dtype == "object" and col not in ["exchange", "symbol", "interval", "source", "source_file", "direction_label"]:
                df_train[col] = df_train[col].astype("category")
                
        self._extract_features(df_train)
        
        y_train = self._map_labels(df_train[self.target])
        w_train = df_train[self.weight_col] if self.weight_col in df_train.columns else None
        
        if cv_splitter is not None:
            logger.info("Starting Optuna Hyperparameter Tuning...")
            self.params = self._tune_hyperparameters(df_train, y_train, w_train, cv_splitter)
            
        # Train final model on ALL training data with best params
        logger.info("Training final LightGBM model on full training set...")
        from finsight.experts.quant.feature_engineering.weighting.class_weight import compute_class_weight
        cw_final = compute_class_weight(df_train, self.target)
        w_final = w_train * cw_final if w_train is not None else cw_final
        train_data = lgb.Dataset(df_train[self.features], label=y_train, weight=w_final)
        
        self.model = lgb.train(
            self.params,
            train_data,
            num_boost_round=self.config.get("num_boost_round", 100)
        )
        
    def _tune_hyperparameters(self, df_train, y_train, w_train, cv_splitter):
        def objective(trial):
            params = {
                "objective": "multiclass",
                "num_class": 3,
                "metric": "multi_logloss",
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
                "num_leaves": trial.suggest_int("num_leaves", 15, 63),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "min_child_samples": trial.suggest_int("min_child_samples", 20, 500),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                "random_state": self.config.get("random_seed", 42),
                "verbose": -1
            }
            
            cv_scores = []
            from finsight.experts.quant.feature_engineering.weighting.class_weight import compute_class_weight
            
            for train_idx, val_idx in cv_splitter.split(df_train):
                df_tr = df_train.iloc[train_idx]
                df_va = df_train.iloc[val_idx]
                X_tr, y_tr = df_tr[self.features], y_train.iloc[train_idx]
                X_va, y_va = df_va[self.features], y_train.iloc[val_idx]
                
                # Tính class weight độc lập trên từng fold train
                cw_tr = compute_class_weight(df_tr, self.target)
                cw_va = df_va[self.target].map(
                    {label: cw_tr.loc[df_tr[self.target] == label].iloc[0] if label in df_tr[self.target].values else 1.0 
                     for label in df_va[self.target].unique()}
                ).fillna(1.0)
                
                w_tr = w_train.iloc[train_idx] * cw_tr if w_train is not None else cw_tr
                w_va = w_train.iloc[val_idx] * cw_va if w_train is not None else cw_va
                
                dtrain = lgb.Dataset(X_tr, label=y_tr, weight=w_tr)
                dval = lgb.Dataset(X_va, label=y_va, weight=w_va, reference=dtrain)
                
                model = lgb.train(
                    params,
                    dtrain,
                    num_boost_round=200,
                    valid_sets=[dval],
                    callbacks=[lgb.early_stopping(stopping_rounds=20, verbose=False)]
                )
                
                cv_scores.append(model.best_score["valid_0"]["multi_logloss"])
                
            return np.mean(cv_scores)

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=self.config.get("optuna_trials", 10))
        
        logger.info(f"Best Optuna Params: {study.best_params}")
        best_params = self.params.copy()
        best_params.update(study.best_params)
        return best_params

    def predict_proba(self, df_test: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model is not trained yet!")
            
        df_test = df_test.copy()
        for col in self.features:
            if df_test[col].dtype == "object":
                df_test[col] = df_test[col].astype("category")
                
        return self.model.predict(df_test[self.features])

    def predict(self, df_test: pd.DataFrame) -> np.ndarray:
        proba = self.predict_proba(df_test)
        preds_idx = np.argmax(proba, axis=1)
        reverse_mapping = {0: "BEARISH", 1: "SIDEWAYS", 2: "BULLISH"}
        return np.vectorize(reverse_mapping.get)(preds_idx)

    def save(self, model_dir: str) -> None:
        path = Path(model_dir)
        path.mkdir(parents=True, exist_ok=True)
        self.model.save_model(path / "lightgbm.txt")
        # Save features list
        pd.Series(self.features).to_json(path / "features.json", orient="records")

    @classmethod
    def load(cls, model_dir: str, config: dict) -> "LightGBMQuantModel":
        instance = cls(config)
        path = Path(model_dir)
        instance.model = lgb.Booster(model_file=str(path / "lightgbm.txt"))
        instance.features = pd.read_json(path / "features.json", orient="records").tolist()
        return instance
