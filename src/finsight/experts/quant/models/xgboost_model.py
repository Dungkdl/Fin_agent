"""Triển khai mô hình XGBoost cho Quant Trading."""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import xgboost as xgb
import optuna
import joblib

from finsight.experts.quant.models.interface import BaseQuantModel

logger = logging.getLogger(__name__)

class XGBoostQuantModel(BaseQuantModel):
    def __init__(self, config: dict):
        super().__init__(config)
        self.features = [] 
        self.target = "direction_label"
        self.weight_col = "final_weight"
        
        self.params = {
            "objective": "multi:softprob",
            "num_class": 3,
            "eval_metric": "mlogloss",
            "learning_rate": 0.05,
            "max_depth": 6,
            "random_state": self.config.get("random_seed", 42),
            "enable_categorical": True,
            "n_estimators": self.config.get("num_boost_round", 100),
            "early_stopping_rounds": None
        }

    def _extract_features(self, df: pd.DataFrame):
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
        # Ép kiểu cột object sang category để XGBoost tự động nhận diện (yêu cầu enable_categorical=True)
        for col in df_train.columns:
            if df_train[col].dtype == "object" and col not in ["exchange", "symbol", "interval", "source", "source_file", "direction_label"]:
                df_train[col] = df_train[col].astype("category")

        self._extract_features(df_train)
        
        y_train = self._map_labels(df_train[self.target])
        w_train = df_train[self.weight_col].values if self.weight_col in df_train.columns else None
        
        if cv_splitter is not None:
            logger.info("Starting Optuna Hyperparameter Tuning for XGBoost...")
            self.params = self._tune_hyperparameters(df_train, y_train, w_train, cv_splitter)
            
        logger.info("Training final XGBoost model on full training set...")
        
        from finsight.experts.quant.feature_engineering.weighting.class_weight import compute_class_weight
        cw_final = compute_class_weight(df_train, self.target).values
        w_final = w_train * cw_final if w_train is not None else cw_final
        
        # Train
        self.model = xgb.XGBClassifier(**self.params)
        self.model.fit(
            df_train[self.features], 
            y_train, 
            sample_weight=w_final,
            verbose=False
        )
        
    def _tune_hyperparameters(self, df_train, y_train, w_train, cv_splitter):
        def objective(trial):
            params = {
                "objective": "multi:softprob",
                "num_class": 3,
                "eval_metric": "mlogloss",
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                "random_state": self.config.get("random_seed", 42),
                "enable_categorical": True,
                "n_estimators": 200,
                "early_stopping_rounds": 20
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
                
                w_tr = w_train[train_idx] * cw_tr.values if w_train is not None else cw_tr.values
                w_va = w_train[val_idx] * cw_va.values if w_train is not None else cw_va.values
                
                clf = xgb.XGBClassifier(**params)
                
                clf.fit(
                    X_tr, y_tr, 
                    sample_weight=w_tr,
                    eval_set=[(X_va, y_va)],
                    sample_weight_eval_set=[w_va] if w_va is not None else None,
                    verbose=False
                )
                
                best_score = clf.best_score
                cv_scores.append(best_score)
                
            return np.mean(cv_scores)

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=self.config.get("optuna_trials", 10))
        
        logger.info(f"Best Optuna Params (XGBoost): {study.best_params}")
        best_params = self.params.copy()
        best_params.update(study.best_params)
        
        # Nếu đã tune thì lúc train final bỏ early stopping
        if "early_stopping_rounds" in best_params:
            best_params["early_stopping_rounds"] = None
            
        return best_params

    def cross_val_predict(self, df_train: pd.DataFrame, cv_splitter) -> np.ndarray:
        logger.info("Sinh Walk-Forward Out-Of-Fold probabilities cho XGBoost...")
        df_train = df_train.copy()
        for col in self.features:
            if df_train[col].dtype == "object":
                df_train[col] = df_train[col].astype("category")
                
        y_train = self._map_labels(df_train[self.target])
        w_train = df_train[self.weight_col].values if self.weight_col in df_train.columns else None
        
        oof_preds = np.full((len(df_train), 3), np.nan)
        from finsight.experts.quant.feature_engineering.weighting.class_weight import compute_class_weight
        
        for train_idx, val_idx in cv_splitter.split(df_train):
            df_tr = df_train.iloc[train_idx]
            df_va = df_train.iloc[val_idx]
            X_tr, y_tr = df_tr[self.features], y_train.iloc[train_idx]
            X_va = df_va[self.features]
            
            cw_tr = compute_class_weight(df_tr, self.target)
            w_tr = w_train[train_idx] * cw_tr.values if w_train is not None else cw_tr.values
            
            clf = xgb.XGBClassifier(**self.params)
            clf.fit(
                X_tr, y_tr, 
                sample_weight=w_tr,
                verbose=False
            )
            
            preds = clf.predict_proba(X_va)
            oof_preds[val_idx] = preds
            
        return oof_preds

    def predict_proba(self, df_test: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model is not trained yet!")
            
        df_test = df_test.copy()
        for col in self.features:
            if df_test[col].dtype == "object":
                df_test[col] = df_test[col].astype("category")
                
        return self.model.predict_proba(df_test[self.features])

    def predict(self, df_test: pd.DataFrame) -> np.ndarray:
        proba = self.predict_proba(df_test)
        preds_idx = np.argmax(proba, axis=1)
        reverse_mapping = {0: "BEARISH", 1: "SIDEWAYS", 2: "BULLISH"}
        return np.vectorize(reverse_mapping.get)(preds_idx)

    def save(self, model_dir: str) -> None:
        path = Path(model_dir)
        path.mkdir(parents=True, exist_ok=True)
        
        # Workaround cho lỗi TypeError: `_estimator_type` undefined của thư viện xgboost
        if not hasattr(self.model, "_estimator_type"):
            self.model._estimator_type = "classifier"
            
        self.model.save_model(path / "xgboost.json")
        pd.Series(self.features).to_json(path / "features.json", orient="records")

    @classmethod
    def load(cls, model_dir: str, config: dict) -> "XGBoostQuantModel":
        instance = cls(config)
        path = Path(model_dir)
        
        instance.model = xgb.XGBClassifier()
        instance.model.load_model(path / "xgboost.json")
        instance.features = pd.read_json(path / "features.json", orient="records").tolist()
        
        return instance
