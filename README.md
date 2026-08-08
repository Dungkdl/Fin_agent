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
finsight universe build --quote-asset USDT --limit 10 --dry-run
```

### Giai đoạn 2: Tải và Tinh chế Dữ liệu Thô (Market Backfill)
Sử dụng kho lưu trữ **Bronze/Silver Lake**. Tải toàn bộ nến từ file ZIP (tháng cũ) và nối mượt mà với REST API (tháng hiện tại). Dữ liệu Silver được lưu ở định dạng `Parquet` siêu tối ưu.

```bash
# Tải dữ liệu 3 tháng đầu năm 2023 cho BTC và ETH, khung 15 phút
finsight market backfill --symbols BTCUSDT,ETHUSDT --intervals 15m --start 2023-01-01 --end 2023-03-31 --mode hybrid --no-dry-run
```
*(Cơ chế thông minh: Chạy lại lệnh này nhiều lần sẽ không bị tải lại file ZIP cũ, và dữ liệu lưu xuống Parquet sẽ tự động Upsert chứ không phình to ổ cứng).*

### Giai đoạn 3: Feature Engineering & Dataset Builder 🆕
Khởi tạo dữ liệu Huấn luyện AI (Gold Layer). Hệ thống sẽ đọc file `quant_1d_5d.yaml`, tính toán hơn 60 đặc trưng toán học phức tạp (Momentum, Volatility, Time Cyclical, Market Regime, Cross-asset context BTC/ETH), đánh nhãn và gán trọng số thông minh.

```bash
# Biến đổi nến thô thành tập dữ liệu huấn luyện (Training Dataset)
finsight quant build-dataset --config configs/quant_1d_5d.yaml
```
Đầu ra sẽ là một file `data/gold/crypto_quant_1d_5d.parquet` chứa mọi thứ Model cần để bắt đầu học.

### Giai đoạn 4: Huấn luyện Mô hình & Tuning (Model Training) 🆕
Đưa file dữ liệu `Gold` vào huấn luyện. Hệ thống tự động sử dụng **Walk-Forward Cross Validation** (kỹ thuật cuốn chiếu với Embargo gap) kết hợp với **Optuna** để tìm ra siêu tham số tốt nhất mà tuyệt đối không bị dính lỗi Rò rỉ dữ liệu (Data Leakage).

Đặc biệt, hệ thống sử dụng kiến trúc **Model Registry**, cho phép dễ dàng chuyển đổi linh hoạt qua cấu hình YAML giữa 4 động cơ AI mạnh mẽ:
- **LightGBM** (Mặc định)
- **XGBoost**
- **CatBoost** (Đỉnh cao xử lý dữ liệu categorical)
- **Logistic Regression** (Sử dụng làm Baseline Model)

```bash
# (Sắp ra mắt lệnh CLI: finsight quant train --config configs/quant_1d_5d.yaml)
```
Kết quả của Phase 4 là mô hình AI hoàn chỉnh được lưu tại `artifacts/models/crypto/crypto_quant_1d_5d/v1/`.

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
