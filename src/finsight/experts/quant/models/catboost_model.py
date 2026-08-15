"""Triển khai mô hình CatBoost cho Quant Trading."""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from catboost import CatBoostClassifier, Pool
import optuna

from finsight.experts.quant.models.interface import BaseQuantModel

logger = logging.getLogger(__name__)

class CatBoostQuantModel(BaseQuantModel):
    def __init__(self, config: dict):
        super().__init__(config)
        self.features = [] 
        self.categorical_features = []
        self.target = "direction_label"
        self.weight_col = "final_weight"
        
        self.params = {
            "loss_function": "MultiClass",
            "eval_metric": "MultiClass",
            "learning_rate": 0.05,
            "depth": 6,
            "random_seed": self.config.get("random_seed", 42),
            "iterations": self.config.get("num_boost_round", 100),
            "verbose": False,
            "early_stopping_rounds": None,
            "thread_count": -1,
            "allow_writing_files": False
        }

    def _extract_features(self, df: pd.DataFrame):
        exclude_cols = [
            "exchange", "symbol", "interval", "open_time", "close_time", 
            "source", "source_file", "quality_status", "quality_flags",
            "future_return", "normalized_return", "direction_label",
            "class_weight", "recency_weight", "regime_weight", "quality_weight", "final_weight"
        ]
        self.features = [c for c in df.columns if c not in exclude_cols]
        
        # Xác định categorical features để báo cho CatBoost
        self.categorical_features = [c for c in self.features if df[c].dtype == "object" or pd.api.types.is_categorical_dtype(df[c])]
        
    def _map_labels(self, labels: pd.Series) -> pd.Series:
        mapping = {"BEARISH": 0, "SIDEWAYS": 1, "BULLISH": 2}
        return labels.map(mapping)

    def train(self, df_train: pd.DataFrame, cv_splitter=None) -> None:
        # Fill NaN cho categorical features vì CatBoost không tự xử lý NaN trong object cột
        for col in df_train.columns:
            if df_train[col].dtype == "object" and col not in ["exchange", "symbol", "interval", "source", "source_file", "direction_label"]:
                df_train[col] = df_train[col].fillna("Unknown").astype(str)

        self._extract_features(df_train)
        
        y_train = self._map_labels(df_train[self.target])
        w_train = df_train[self.weight_col].values if self.weight_col in df_train.columns else None
        
        if cv_splitter is not None:
            logger.info("Starting Optuna Hyperparameter Tuning for CatBoost...")
            self.params = self._tune_hyperparameters(df_train, y_train, w_train, cv_splitter)
            
        logger.info("Training final CatBoost model on full training set...")
        
        from finsight.experts.quant.feature_engineering.weighting.class_weight import compute_class_weight
        cw_final = compute_class_weight(df_train, self.target).values
        w_final = w_train * cw_final if w_train is not None else cw_final
        
        train_pool = Pool(
            data=df_train[self.features], 
            label=y_train, 
            weight=w_final,
            cat_features=self.categorical_features
        )
        
        self.model = CatBoostClassifier(**self.params)
        self.model.fit(train_pool, verbose=False)
        logger.info(f"[Verification] Actual CatBoost trees built: {self.model.tree_count_}")
        
    def _tune_hyperparameters(self, df_train, y_train, w_train, cv_splitter):
        def objective(trial):
            params = {
                "loss_function": "MultiClass",
                "eval_metric": "MultiClass",
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
                "depth": trial.suggest_int("depth", 4, 10),
                "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 10),
                "random_seed": self.config.get("random_seed", 42),
                "iterations": 200,
                "early_stopping_rounds": 20,
                "verbose": False,
                "thread_count": -1,
                "allow_writing_files": False
            }
            
            cv_scores = []
            best_iters = []
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
                
                train_pool = Pool(X_tr, label=y_tr, weight=w_tr, cat_features=self.categorical_features)
                val_pool = Pool(X_va, label=y_va, weight=w_va, cat_features=self.categorical_features)
                
                clf = CatBoostClassifier(**params)
                
                clf.fit(train_pool, eval_set=val_pool, verbose=False)
                
                # Retrieve best score
                best_score = clf.get_best_score()["validation"]["MultiClass"]
                cv_scores.append(best_score)
                best_iters.append(clf.get_best_iteration())
                
            trial.set_user_attr("best_iteration", int(np.median(best_iters)))
            return np.mean(cv_scores)

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=self.config.get("optuna_trials", 10))
        
        logger.info(f"Best Optuna Params (CatBoost): {study.best_params}")
        best_params = self.params.copy()
        best_params.update(study.best_params)
        
        # Đồng bộ Boosting Rounds
        best_iteration = study.best_trial.user_attrs.get("best_iteration", None)
        if best_iteration is not None:
            best_params["iterations"] = best_iteration
        
        if "early_stopping_rounds" in best_params:
            best_params["early_stopping_rounds"] = None
            
        return best_params

    def cross_val_predict(self, df_train: pd.DataFrame, cv_splitter) -> np.ndarray:
        logger.info("Sinh Walk-Forward Out-Of-Fold probabilities cho CatBoost...")
        df_train = df_train.copy()
        for col in df_train.columns:
            if df_train[col].dtype == "object" and col not in ["exchange", "symbol", "interval", "source", "source_file", "direction_label"]:
                df_train[col] = df_train[col].fillna("Unknown").astype(str)
                
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
            
            train_pool = Pool(X_tr, label=y_tr, weight=w_tr, cat_features=self.categorical_features)
            
            clf = CatBoostClassifier(**self.params)
            clf.fit(train_pool, verbose=False)
            
            preds = clf.predict_proba(X_va)
            oof_preds[val_idx] = preds
            
        return oof_preds

    def predict_proba(self, df_test: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model is not trained yet!")
            
        df_test = df_test.copy()
        for col in self.categorical_features:
            df_test[col] = df_test[col].fillna("Unknown").astype(str)
                
        return self.model.predict_proba(df_test[self.features])

    def predict(self, df_test: pd.DataFrame) -> np.ndarray:
        proba = self.predict_proba(df_test)
        preds_idx = np.argmax(proba, axis=1)
        reverse_mapping = {0: "BEARISH", 1: "SIDEWAYS", 2: "BULLISH"}
        return np.vectorize(reverse_mapping.get)(preds_idx)

    def save(self, model_dir: str) -> None:
        path = Path(model_dir)
        path.mkdir(parents=True, exist_ok=True)
        self.model.save_model(str(path / "catboost.cbm"))
        
        meta = {
            "features": self.features,
            "categorical_features": self.categorical_features
        }
        pd.Series(meta).to_json(path / "features.json")

    @classmethod
    def load(cls, model_dir: str, config: dict) -> "CatBoostQuantModel":
        instance = cls(config)
        path = Path(model_dir)
        
        instance.model = CatBoostClassifier()
        instance.model.load_model(str(path / "catboost.cbm"))
        
        meta = pd.read_json(path / "features.json", typ="series")
        instance.features = meta["features"]
        instance.categorical_features = meta["categorical_features"]
        
        return instance
