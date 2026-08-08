# FinSight Agent - Chuyên gia phân tích lượng tử Crypto

FinSight Agent là một dự án phân tích thị trường tập trung vào nghiên cứu (research-first). Mã nguồn hiện tại chứa nền tảng của **Giai đoạn 0, Giai đoạn 1 và Giai đoạn 2** cho hệ thống Crypto Quant Expert v1.

## Phạm vi dự án

- **Loại tài sản:** Tiền mã hóa (Crypto)
- **Sàn giao dịch:** Binance
- **Chế độ giao dịch:** Chỉ Spot (Giao ngay)
- **Đồng định giá (Quote asset):** USDT
- **Các cặp giao dịch bắt buộc (Required):** BTCUSDT, ETHUSDT
- **Các cặp giao dịch tiềm năng (Candidate):** SOLUSDT, BNBUSDT, XRPUSDT, ADAUSDT, DOGEUSDT, LINKUSDT

> **Lưu ý:** Dự án này không gọi bất kỳ API nào để đặt lệnh giao dịch, không yêu cầu cấp quyền giao dịch (trading permissions), và không đưa ra lời khuyên tài chính.

## Hướng dẫn cài đặt và chạy Code

Dự án này sử dụng `pyproject.toml` để quản lý các gói phụ thuộc (dependencies) và đóng gói mã nguồn. Việc cài đặt qua môi trường ảo (venv) sẽ giúp bạn chạy code dễ dàng hơn, không cần phải cấu hình biến môi trường `PYTHONPATH` thủ công nữa.

### 1. Cài đặt môi trường (Venv)

Mở terminal (PowerShell) tại thư mục dự án và chạy các lệnh sau:

```powershell
# Tạo môi trường ảo có tên là .venv
python -m venv .venv

# Kích hoạt môi trường ảo
.\.venv\Scripts\Activate.ps1

# Cài đặt dự án cùng các thư viện phát triển (dev dependencies) từ pyproject.toml
pip install -e .[dev]
```

*(Lưu ý: Nếu bạn dùng Linux/macOS, lệnh kích hoạt sẽ là `source .venv/bin/activate`)*

### 2. Quản lý danh sách Coin (Universe) - Giai đoạn 1

Sau khi cài đặt, lệnh `finsight` sẽ được liên kết trực tiếp vào hệ thống của bạn.

Chọn lọc và xây dựng danh sách các cặp coin đạt tiêu chuẩn (đủ volume, thanh khoản tốt) từ Binance:

```bash
finsight universe build --quote-asset USDT --limit 10
```

Thêm cờ `--dry-run` để chỉ xem trước kết quả trên màn hình mà không cần lưu ra file báo cáo:

```bash
finsight universe build --quote-asset USDT --limit 10 --dry-run
```

### 3. Tải và tinh chế dữ liệu thị trường (Market Backfill) - Giai đoạn 2

Hệ thống có khả năng tải dữ liệu lịch sử cực lớn (ZIP file) kết hợp với dữ liệu cập nhật mới nhất (REST API), sau đó tự động **chuẩn hóa**, **loại bỏ trùng lặp**, **đánh giá chất lượng** và lưu vào định dạng siêu nhẹ **Silver Parquet**.

Để tải dữ liệu thực tế (Ví dụ: dữ liệu 15m cho BTCUSDT trong tháng 1/2023), hãy chạy lệnh sau:

```bash
finsight market backfill --symbols BTCUSDT --intervals 15m --start 2023-01-01 --end 2023-01-31 --mode hybrid --no-dry-run
```

**Các chế độ chạy (`--mode`):**
- `monthly-zip`: Chỉ tải file nén lịch sử theo tháng của Binance.
- `rest`: Cập nhật dữ liệu mới nhất trực tiếp qua API (giới hạn số lượng nến).
- `hybrid` (Khuyên dùng): Tải cả ZIP và REST, sau đó tự động nối lại thành một chuỗi thời gian hoàn chỉnh không đứt gãy.

**Kiến trúc lưu trữ Data Lake:**
👉 **Lớp Bronze (Dữ liệu thô):** `data/bronze/binance/spot/klines/` (Nơi chứa các file `.zip` và `.csv` gốc).
👉 **Lớp Silver (Dữ liệu tinh chế):** `data/silver/candles/` (Nơi chứa dữ liệu Parquet đã được loại bỏ nến trùng, sẵn sàng cho Machine Learning, được phân mảnh theo cấu trúc `exchange/symbol/interval/year/month`).

> [!WARNING]
> **Lỗi UnicodeEncodeError trên PowerShell (Windows)**
> Nếu đường dẫn thư mục dự án của bạn có chứa tiếng Việt có dấu (ví dụ: `D:\Tự học\AI\...`), terminal PowerShell có thể bị crash khi cố in đường dẫn file ra màn hình. Mặc dù dữ liệu vẫn được tải thành công, nhưng để tránh bị văng lỗi đỏ, bạn hãy chạy lệnh sau để ép PowerShell dùng UTF-8 trước khi gọi `finsight`:
> ```powershell
> $env:PYTHONIOENCODING="utf-8"
> ```

## Chạy bộ kiểm thử (Tests)

Chỉ cần gọi lệnh sau để chạy toàn bộ Unit Tests kiểm tra độ bền bỉ của hệ thống:

```bash
pytest
```

## Cấu trúc Mã nguồn

- Xem chi tiết bố cục thư mục dựa theo tài liệu thiết kế tại: `docs/code_structure.md`
- Xem giải thích chi tiết chức năng của từng file và luồng phụ thuộc tại: `docs/quant_expert_file_map.md`
- Hướng dẫn cách đọc hiểu code: `docs/how_to_read_quant_expert_code.md`
- Tài liệu về Kiến trúc đa chuyên gia (Multi-expert architecture): `docs/multi_expert_architecture.md`
