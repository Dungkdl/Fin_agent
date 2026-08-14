"""Sinh báo cáo Model Card và tổng hợp kết quả (Metrics, Backtest, SHAP)."""

import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_model_card(model_dir: Path, config: dict, metrics: dict, backtest: dict, shap_imp: list):
    """Tạo file model_card.md theo chuẩn tài liệu."""
    model_name = config.get("model_name", "crypto_quant_model")
    
    top_features = "\n".join([f"- **{f['feature']}**: {f['shap_importance']:.4f}" for f in shap_imp[:10]])
    
    content = f"""# Model Card: {model_name}

## 1. Model Details
- **Version**: v1
- **Created At**: {datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
- **Algorithm**: {config.get('model', {}).get('type', 'lightgbm')}
- **Task**: Multi-class Classification (BEARISH, SIDEWAYS, BULLISH)

## 2. Intended Use
- **Primary Use Case**: Phân tích định lượng và dự báo xu hướng tài sản Crypto trên thị trường Binance Spot.
- **Input Interval**: {config.get('input_interval', '15m')}
- **Forecast Horizon**: {config.get('forecast_horizon', '1h')}
- **Out-of-Scope**: Không sử dụng cho thị trường Futures, không chạy trên dữ liệu tick, không tự động giao dịch tiền thật.

## 3. Metrics (Final Holdout)
- **Macro F1**: {metrics.get('macro_f1', 0):.4f}
- **Log Loss**: {metrics.get('log_loss', 0):.4f}
- **Balanced Accuracy**: {metrics.get('balanced_accuracy', 0):.4f}

## 4. Spot-safe Backtest Simulation
*(Mô phỏng Giao dịch: Chỉ Long, bỏ qua Short, áp dụng Slippage & Fee)*
- **Net Return**: {backtest.get('net_return', 0):.2%}
- **Win Rate**: {backtest.get('win_rate', 0):.2%}
- **Max Drawdown**: {backtest.get('max_drawdown', 0):.2%}
- **Total Trades**: {backtest.get('total_trades', 0)}
- **Pseudo Sharpe Ratio**: {backtest.get('pseudo_sharpe_ratio', 0):.2f}

## 5. Feature Importance (Top 10 SHAP)
{top_features}

## 6. Caveats and Recommendations
- **Disclaimer**: KHÔNG PHẢI LỜI KHUYÊN TÀI CHÍNH. Kết quả backtest trong quá khứ không đảm bảo hiệu suất trong tương lai.
- **Recommendation**: Cần kết hợp chung với Fusion Model, Risk Engine và Fundamental Analysis.
"""
    with open(model_dir / "model_card.md", "w", encoding="utf-8") as f:
        f.write(content)
        
    logger.info("Đã tạo model_card.md thành công.")


def save_reports(model_dir: str, config: dict, metrics: dict, slices: dict, backtest: dict, shap_imp: list):
    """Lưu toàn bộ json metrics và tạo model card."""
    path = Path(model_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    # Lưu metrics.json
    full_metrics = {
        "global": metrics,
        "slices": slices,
        "backtest_simulation": backtest
    }
    with open(path / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(full_metrics, f, indent=2, ensure_ascii=False)
        
    # Lưu model_card.md
    generate_model_card(path, config, metrics, backtest, shap_imp)
