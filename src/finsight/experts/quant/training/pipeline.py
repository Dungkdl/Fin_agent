"""Pipeline điều phối quá trình huấn luyện và đánh giá mô hình."""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import warnings

from finsight.experts.quant.models.registry import get_quant_model
from finsight.experts.quant.models.splitters.walk_forward import WalkForwardSplitter

logger = logging.getLogger(__name__)

class TrainingPipeline:
    def __init__(self, config: dict, data_path: Path):
        self.config = config
        self.data_path = Path(data_path)
        
        # Parse configs
        val_config = config.get("validation", {})
        self.min_train_months = val_config.get("min_train_months", 12)
        self.validation_months = val_config.get("validation_months", 3)
        self.step_months = val_config.get("step_months", 3)
        self.final_holdout_months = val_config.get("final_holdout_months", 3)
        
        # Sử dụng Factory pattern để lấy đúng model từ file YAML config
        self.model = get_quant_model(config.get("model", {}))
        
        # Khởi tạo splitter, forecast_horizon = embargo_steps (quy đổi tương đối, giả sử 5 nến = 5)
        # Trong thực tế, embargo_steps phải đổi từ time string (e.g. "5d") sang số nến hoặc dùng date offset.
        # Ở đây ta giả định embargo = forecast_steps từ config
        self.embargo_steps = config.get("forecast_steps", 5)
        self.input_interval = config.get("input_interval", "1d")
        self.splitter = WalkForwardSplitter(
            min_train_months=self.min_train_months,
            validation_months=self.validation_months,
            step_months=self.step_months,
            embargo_steps=self.embargo_steps,
            input_interval=self.input_interval
        )

    def run(self):
        logger.info(f"Đọc dữ liệu từ {self.data_path}")
        df = pd.read_parquet(self.data_path)
        df = df.sort_values("close_time").reset_index(drop=True)
        
        # 1. Tách Final Holdout (Tập dữ liệu tối mật, không được dùng để Tuning)
        end_time = df["close_time"].max()
        holdout_start = end_time - pd.DateOffset(months=self.final_holdout_months)
        
        # Embargo cho Holdout
        # Chắc chắn rằng tập Holdout không bị rò rỉ label từ tập Train.
        # Tìm nến cuối cùng của tập Train bằng cách lùi lại embargo_steps từ holdout_start
        holdout_mask = df["close_time"] >= holdout_start
        holdout_idx = df.index[holdout_mask]
        
        if len(holdout_idx) > 0:
            # Chuyển đổi input_interval thành Timedelta (VD: 1d -> 1 days)
            interval_str = self.input_interval.lower()
            if interval_str.endswith('d'):
                td = pd.Timedelta(days=int(interval_str[:-1]))
            elif interval_str.endswith('h'):
                td = pd.Timedelta(hours=int(interval_str[:-1]))
            elif interval_str.endswith('m'):
                td = pd.Timedelta(minutes=int(interval_str[:-1]))
            else:
                td = pd.Timedelta(days=1)
                
            embargo_time = td * self.embargo_steps
            
            # Tập Train phải kết thúc trước thời điểm Holdout bắt đầu trừ đi embargo_time
            train_time_limit = holdout_start - embargo_time
            
            df_train_val = df[df["close_time"] < train_time_limit].copy()
            df_holdout = df[holdout_mask].copy()
            logger.info(f"Tách Final Holdout: {len(df_holdout)} samples. Train/Val: {len(df_train_val)} samples.")
        else:
            warnings.warn("Không đủ dữ liệu để tạo Final Holdout!")
            df_train_val = df.copy()
            df_holdout = pd.DataFrame()
            
        # 2. Huấn luyện mô hình (Kèm Optuna Tuning) trên toàn bộ Train/Val
        logger.info("Bắt đầu huấn luyện mô hình với Walk-Forward CV trên tập Train/Val...")
        self.model.train(df_train_val, cv_splitter=self.splitter)
        
        # 3. Lấy Out-Of-Fold probabilities từ Walk-Forward CV để dò Threshold
        logger.info("Sinh Walk-Forward Out-Of-Fold probabilities...")
        y_prob_oof = self.model.cross_val_predict(df_train_val, cv_splitter=self.splitter)
        
        # 4. Tune Threshold trên OOF probabilities
        logger.info("Tuning Probability Threshold trên tập OOF Validation...")
        # Lọc ra các mẫu có dự đoán (không bị NaN do nằm ngoài các Validation folds)
        valid_mask = ~np.isnan(y_prob_oof[:, 0])
        y_prob_tune = y_prob_oof[valid_mask]
        
        y_true = self.model._map_labels(df_train_val["direction_label"]).values
        y_true_tune = y_true[valid_mask]
        y_true_binary = (y_true_tune == 2).astype(int)
        
        from sklearn.metrics import f1_score
        best_f1 = 0
        best_th = 0.50
        
        if len(y_prob_tune) > 0:
            for th in np.arange(0.34, 0.75, 0.02):
                preds = (y_prob_tune[:, 2] >= th).astype(int)
                f1 = f1_score(y_true_binary, preds, zero_division=0)
                if f1 > best_f1:
                    best_f1 = f1
                    best_th = th
                    
        logger.info(f"Đã Tune Threshold = {best_th:.2f} (OOS F1-BULLISH: {best_f1:.2f}) trên {len(y_prob_tune)} mẫu OOF.")
        if "backtest" not in self.config:
            self.config["backtest"] = {}
        self.config["backtest"]["probability_threshold"] = float(best_th)
        
        # 6. Lưu mô hình
        model_dir = f"artifacts/models/crypto/{self.config.get('model_name', 'default_model')}/v1"
        logger.info(f"Lưu mô hình tại {model_dir}")
        self.model.save(model_dir)
        
        # 5. Đánh giá sơ bộ trên Holdout (Nếu có)
        if not df_holdout.empty:
            from finsight.experts.quant.training.evaluation import evaluate_classification, evaluate_slices
            from finsight.experts.quant.training.backtest import run_spot_backtest
            from finsight.experts.quant.training.shap_explainer import explain_model_with_shap
            from finsight.experts.quant.training.report import save_reports
            
            logger.info("Chạy Evaluate Metrics trên Final Holdout (Untouched Data)...")
            y_prob = self.model.predict_proba(df_holdout)
            
            # Classification Evaluation MUST use argmax, strictly separated from Trading Threshold
            y_pred_class = np.argmax(y_prob, axis=1)
            
            y_true = self.model._map_labels(df_holdout["direction_label"]).values
            
            metrics = evaluate_classification(y_true, y_pred_class, y_prob)
            slices = evaluate_slices(df_holdout, y_true, y_pred_class, y_prob)
            
            logger.info(f"Balanced Acc (Holdout): {metrics['balanced_accuracy']:.2%} | Macro F1: {metrics['macro_f1']:.2f}")
            logger.info(f"Log Loss: {metrics['log_loss']:.3f} | Brier Score: {metrics['brier_score']:.3f}")
            logger.info(f"Precision: {metrics['per_class_precision']}")
            logger.info(f"Recall: {metrics['per_class_recall']}")
            logger.info(f"Confusion Matrix:\n{np.array(metrics['confusion_matrix'])}")
            
            logger.info("Chạy Spot-safe Backtest Simulation...")
            # Gắn xác suất vào DF để chạy giả lập
            df_sim = df_holdout.copy()
            df_sim["prob_BEARISH"] = y_prob[:, 0]
            df_sim["prob_SIDEWAYS"] = y_prob[:, 1]
            df_sim["prob_BULLISH"] = y_prob[:, 2]
            
            bt_config = {**self.config.get("backtest", {}), "forecast_steps": self.config.get("forecast_steps", 5)}
            backtest_results = run_spot_backtest(df_sim, bt_config)
            
            logger.info("=== KẾT QUẢ BACKTEST (MARK-TO-MARKET PORTFOLIO) ===")
            logger.info(f"Final Equity  : {backtest_results['final_equity']:.4f}")
            logger.info(f"Net Return    : {backtest_results['net_return']:.2%}")
            logger.info(f"B&H Baseline  : {backtest_results['baseline_return']:.2%}")
            logger.info(f"Max Drawdown  : {backtest_results['max_drawdown']:.2%}")
            logger.info(f"Sharpe Ratio  : {backtest_results['pseudo_sharpe_ratio']:.2f}")
            logger.info(f"Win Rate      : {backtest_results['win_rate']:.2%}")
            logger.info(f"Total Trades  : {backtest_results['total_trades']}")
            logger.info(f"Avg Trade Ret : {backtest_results['average_trade_return']:.2%}")
            logger.info("==================================================")
            
            logger.info("Chạy phân tích SHAP Feature Importance...")
            shap_imp = explain_model_with_shap(
                self.model.model, 
                df_holdout, 
                self.model.features, 
                Path(model_dir)
            )
            
            logger.info("Lưu báo cáo tổng hợp (Model Card & JSON)...")
            save_reports(model_dir, self.config, metrics, slices, backtest_results, shap_imp)
            
        return model_dir
