# FinSight Agent - Chuyên gia phân tích lượng tử Crypto

FinSight Agent là một hệ thống phân tích thị trường tài chính dựa trên dữ liệu (research-first). Dự án đang được phát triển theo kiến trúc **Modular Monolith** (Đa chuyên gia), trong đó **Crypto Quant Expert v1** là chuyên gia đầu tiên được xây dựng để dự báo xu hướng giá Crypto.

Dự án hiện tại đã hoàn thành **Giai đoạn 1, 2, 3 và 4**, bao gồm: Quản lý danh mục (Universe), Tải & Tinh chế dữ liệu thô (Market Backfill), Trích xuất Đặc trưng (Feature Engineering) và Huấn luyện Mô hình AI bằng Walk-Forward CV (Model Training).

## 1. Phạm vi dự án
- **Thị trường:** Binance Spot (Giao ngay)
- **Tài sản định giá:** USDT (BTCUSDT, ETHUSDT...)
- **Dữ liệu:** Dữ liệu nến (Klines/Candles) lịch sử từ Binance Public Data (ZIP) và Binance REST API.
- **Tiêu chí:** Tuyệt đối không dùng dữ liệu tương lai (No future leakage) trong quá trình tính toán chỉ số.

> **Lưu ý:** Dự án này chuyên dùng để Research, Backtest và Evaluation mô hình AI. Không gọi API đặt lệnh thật, không đưa ra lời khuyên tài chính.

---

## 2. Cấu trúc Dự án (Project Structure)

Dự án tuân theo kiến trúc Clean Architecture để dễ dàng mở rộng nhiều AI Expert khác nhau (News, Fundamental, Fusion...):

```text
finsight-agent/
├── configs/                 # Thư mục chứa YAML config điều khiển hệ thống
│   ├── ingestion.yaml       # Cấu hình tải dữ liệu thô
│   └── quant_1d_5d.yaml     # "Bộ não" cấu hình Feature & Model cho AI
├── data/
│   ├── bronze/              # Lớp dữ liệu thô (ZIP, CSV gốc từ Binance)
│   ├── silver/candles/      # Lớp dữ liệu tinh chế (Parquet, đã gộp và xóa trùng lặp)
│   └── gold/                # Lớp dữ liệu vàng (Dataset đã tính Features, Labels, Weights)
├── src/finsight/
│   ├── cli/                 # Chứa các lệnh Terminal (universe, market, quant)
│   ├── config/              # Khởi tạo Settings, Logging, Constants
│   ├── crawl/               # Logic tải dữ liệu từ Binance (ZIP & REST)
│   ├── database/            # Logic kết nối file Storage (Parquet Storage)
│   ├── domain/              # Các Data Models và Enums cốt lõi
│   ├── utils/               # Tiện ích thời gian (timezone-aware)
│   └── experts/             # ✨ Nơi trú ngụ của các Chuyên gia AI
│       ├── fundamental/     # (Dự kiến) Chuyên gia Phân tích Cơ bản
│       ├── news/            # (Dự kiến) Chuyên gia Đọc tin tức
│       ├── fusion/          # (Dự kiến) Chuyên gia Tổng hợp
│       └── quant/           # Chuyên gia Phân tích Định lượng (Hoàn thành Phase 4)
│           ├── datasets/    # Orchestrator xuất file Gold Parquet
│           ├── feature_engineering/ # Logic tính toán Features, Labels, Weights
│           ├── models/      # Kiến trúc Base Model, LightGBM, Splitters (Chống Data Leakage)
│           └── training/    # Pipeline huấn luyện, Optuna tuning và lưu trữ Model
└── tests/                   # Bộ Unit Test (Pytest) đảm bảo độ bền bỉ
```

---

## 3. Hướng dẫn Cài đặt Môi trường

Dự án dùng `pyproject.toml`. Việc dùng môi trường ảo (`.venv`) là bắt buộc để tránh xung đột thư viện.

```powershell
# 1. Tạo môi trường ảo
python -m venv .venv

# 2. Kích hoạt môi trường ảo (PowerShell)
.\.venv\Scripts\Activate.ps1
# (Trên macOS/Linux dùng: source .venv/bin/activate)

# 3. Cài đặt toàn bộ dependencies (bao gồm Pytest để chạy test)
pip install -e .[dev]
# Lưu ý: Cài đặt gói `PyYAML` nếu hệ thống thiếu
pip install pyyaml
```

---

## 4. Các Giai đoạn Hoạt động (Quy trình sử dụng)

Sau khi cài đặt, bạn sử dụng công cụ qua câu lệnh `finsight`. Dưới đây là 3 bước cốt lõi:

### Giai đoạn 1: Xây dựng Danh mục (Universe)
Tự động quét API Binance để tìm các đồng Coin đạt chuẩn (Khối lượng giao dịch lớn, đang hoạt động).

```bash
finsight universe build --quote-asset USDT --limit 10
```

### Giai đoạn 2: Tải và Tinh chế Dữ liệu Thô (Market Backfill)
Lấy dữ liệu nến (Klines) từ Binance. Ở đây ta lấy khung ngày (`1d`) trong **5 năm gần nhất** cho nhiều đồng tiền điện tử hàng đầu (Top Crypto) để đảm bảo mô hình có đủ dữ liệu học hỏi các chu kỳ thị trường khác nhau. Dữ liệu Silver được lưu ở định dạng `Parquet` siêu tối ưu.

```bash
# Tải dữ liệu 5 năm (Từ 2021-08-15 đến hiện tại) cho 11 đồng coin top đầu, khung 1 ngày (1d)
finsight market backfill --symbols BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,DOTUSDT,MATICUSDT,AVAXUSDT,LINKUSDT --intervals 1d --start 2021-08-15 --end 2026-08-15 --mode rest --no-dry-run
```

### Giai đoạn 3: Feature Engineering & Dataset Builder 🆕
Khởi tạo dữ liệu Huấn luyện AI (Gold Layer). Hệ thống sẽ đọc file `quant_1d_5d.yaml`, tính toán hơn 60 đặc trưng toán học phức tạp (Momentum, Volatility, Time Cyclical, Market Regime, Cross-asset context), đánh nhãn và gán trọng số thông minh.

```bash
# Biến đổi nến thô thành tập dữ liệu huấn luyện (Training Dataset)
finsight quant build-dataset --config configs/quant_1d_5d.yaml
```
Đầu ra sẽ là một file `data/gold/training_samples/crypto_quant_1d_5d.parquet` chứa mọi thứ Model cần.

### Giai đoạn 4: Huấn luyện Mô hình & Tuning (Model Training) 🆕
Đưa file dữ liệu `Gold` vào huấn luyện. Hệ thống tự động sử dụng **Walk-Forward Cross Validation** kết hợp với **Optuna** để tìm siêu tham số tốt nhất. Hỗ trợ **Model Registry** (LightGBM, XGBoost, CatBoost, Logistic Regression).

```bash
# Huấn luyện 1 mô hình bất kỳ (vd: XGBoost) từ file config gốc
finsight quant train --config configs/quant_1d_5d.yaml --engine xgboost

# HOẶC: Chạy huấn luyện HÀNG LOẠT tất cả 4 mô hình (Khuyên dùng)
finsight quant train-all
```

Kết quả của Phase 4 là mô hình AI hoàn chỉnh, báo cáo `metrics.json` và diễn giải `shap_importance.json` được tự động lưu tại `artifacts/models/crypto/<model_name>/v1/`.

### Giai đoạn 5: Vận hành Thực tế (Live Updates) 🆕
Mỗi khi bạn muốn lấy dữ liệu nến mới nhất của ngày hôm nay để cập nhật cho Model, bạn không cần chạy lại từ đầu. Hệ thống Hỗ trợ **Incremental Backfill** (Tải bù thông minh):

```bash
# 1. Tải bù nến từ ngày cũ đến hôm nay (Ví dụ từ 2024-01-01 -> 2026-08-15)
finsight market backfill --symbols BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT --intervals 1d --start 2024-01-01 --end 2026-08-15 --mode rest --no-dry-run

# 2. Build lại dữ liệu (tính toán Features cho nến mới)
finsight quant build-dataset --config configs/quant_1d_5d.yaml

# 3. Train lại toàn bộ AI với trí khôn mới nhất
finsight quant train-all
```

---

## 5. Khắc phục Sự cố (Troubleshooting)

1. **Lỗi `Cannot find module` trong VS Code:**
   - Bấm vào góc phải dưới màn hình VS Code (chỗ chọn Python version).
   - Chọn `Select Interpreter` -> Chỉ đường dẫn tới `.\.venv\Scripts\python.exe`.

2. **Lỗi `UnicodeEncodeError` trên PowerShell (Windows):**
   - Xảy ra khi đường dẫn thư mục chứa tiếng Việt (vd: `D:\Tự học\AI\...`).
   - Chạy lệnh này trước khi gõ các lệnh `finsight`:
     ```powershell
     $env:PYTHONIOENCODING="utf-8"
     ```

## 6. Chạy Kiểm thử (Tests)
Chạy toàn bộ kịch bản kiểm định chất lượng:
```bash
pytest
```
*(Hiện tại hệ thống đã pass toàn bộ 22 bài Test).*
