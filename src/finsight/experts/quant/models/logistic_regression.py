"""Triển khai Baseline Model bằng Logistic Regression."""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import optuna
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import log_loss

from finsight.experts.quant.models.interface import BaseQuantModel

logger = logging.getLogger(__name__)

class LogisticRegressionQuantModel(BaseQuantModel):
    def __init__(self, config: dict):
        super().__init__(config)
        self.features = [] 
        self.target = "direction_label"
        self.weight_col = "final_weight"
        
        self.params = {
            "penalty": "l2",
            "C": 1.0,
            "max_iter": 1000,
            "random_state": self.config.get("random_seed", 42),
            "solver": "lbfgs"
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
        
    def _build_sklearn_pipeline(self, df_train: pd.DataFrame):
        # Identify categorical vs numeric features
        categorical_features = []
        numeric_features = []
        
        for col in self.features:
            if df_train[col].dtype == "object" or pd.api.types.is_categorical_dtype(df_train[col]):
                categorical_features.append(col)
            else:
                numeric_features.append(col)
                
        # StandardScaler cho numeric, OneHotEncoder cho categorical
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
            ]
        )
        return preprocessor

    def train(self, df_train: pd.DataFrame, cv_splitter=None) -> None:
        self._extract_features(df_train)
        y_train = self._map_labels(df_train[self.target])
        w_train = df_train[self.weight_col].values if self.weight_col in df_train.columns else None
        
        if cv_splitter is not None:
            logger.info("Starting Optuna Hyperparameter Tuning for Logistic Regression...")
            self.params = self._tune_hyperparameters(df_train, y_train, w_train, cv_splitter)
            
        logger.info("Training final Logistic Regression model on full training set...")
        preprocessor = self._build_sklearn_pipeline(df_train)
        
        clf = LogisticRegression(**self.params)
        self.model = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", clf)])
        
        # Train
        fit_params = {}
        if w_train is not None:
            fit_params["classifier__sample_weight"] = w_train
            
        self.model.fit(df_train[self.features], y_train, **fit_params)
        
    def _tune_hyperparameters(self, df_train, y_train, w_train, cv_splitter):
        preprocessor = self._build_sklearn_pipeline(df_train)
        
        def objective(trial):
            params = {
                "penalty": "l2",
                "C": trial.suggest_float("C", 1e-4, 1e2, log=True),
                "max_iter": 2000,
                "random_state": self.config.get("random_seed", 42),
                "solver": "lbfgs"
            }
            
            cv_scores = []
            
            for train_idx, val_idx in cv_splitter.split(df_train):
                X_tr, y_tr = df_train.iloc[train_idx][self.features], y_train.iloc[train_idx]
                X_va, y_va = df_train.iloc[val_idx][self.features], y_train.iloc[val_idx]
                
                w_tr = w_train[train_idx] if w_train is not None else None
                w_va = w_train[val_idx] if w_train is not None else None
                
                clf = LogisticRegression(**params)
                pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", clf)])
                
                fit_params = {}
                if w_tr is not None:
                    fit_params["classifier__sample_weight"] = w_tr
                    
                pipeline.fit(X_tr, y_tr, **fit_params)
                
                # Evaluate Log loss
                proba = pipeline.predict_proba(X_va)
                loss = log_loss(y_va, proba, labels=[0, 1, 2], sample_weight=w_va)
                cv_scores.append(loss)
                
            return np.mean(cv_scores)

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=self.config.get("optuna_trials", 10))
        
        logger.info(f"Best Optuna Params (Logistic Regression): {study.best_params}")
        best_params = self.params.copy()
        best_params.update(study.best_params)
        return best_params

    def predict_proba(self, df_test: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model is not trained yet!")
        return self.model.predict_proba(df_test[self.features])

    def predict(self, df_test: pd.DataFrame) -> np.ndarray:
        proba = self.predict_proba(df_test)
        preds_idx = np.argmax(proba, axis=1)
        reverse_mapping = {0: "BEARISH", 1: "SIDEWAYS", 2: "BULLISH"}
        return np.vectorize(reverse_mapping.get)(preds_idx)

    def save(self, model_dir: str) -> None:
        path = Path(model_dir)
        path.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path / "logistic_regression.joblib")
        pd.Series(self.features).to_json(path / "features.json", orient="records")

    @classmethod
    def load(cls, model_dir: str, config: dict) -> "LogisticRegressionQuantModel":
        instance = cls(config)
        path = Path(model_dir)
        instance.model = joblib.load(path / "logistic_regression.joblib")
        instance.features = pd.read_json(path / "features.json", orient="records").tolist()
        return instance
