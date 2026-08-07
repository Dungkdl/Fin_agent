# FinSight Agent - Chuyên gia phân tích lượng tử Crypto

FinSight Agent là một dự án phân tích thị trường tập trung vào nghiên cứu (research-first). Mã nguồn hiện tại chứa nền tảng của Giai đoạn 0 và Giai đoạn 1 cho hệ thống Crypto Quant Expert v1.

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

### 2. Quản lý danh sách Coin (Universe)

Sau khi cài đặt bằng `pip install -e .`, lệnh `finsight` sẽ được cài sẵn vào môi trường ảo của bạn (được định nghĩa trong `[project.scripts]`). Bạn có thể gọi trực tiếp lệnh này!

Chọn lọc và xây dựng danh sách các cặp coin đạt tiêu chuẩn từ Binance:

```bash
finsight universe build --quote-asset USDT --limit 10
```

Thêm cờ `--dry-run` để chỉ xem trước kết quả trên màn hình mà không cần lưu ra file báo cáo:

```bash
finsight universe build --quote-asset USDT --limit 10 --dry-run
```

### 3. Tải dữ liệu thị trường (Market Backfill)

Lên kế hoạch và tải dữ liệu giá lịch sử (klines) cho các cặp coin.

Ví dụ: xem trước danh sách các file sẽ tải cho BTCUSDT và ETHUSDT (khung 15m và 1h, từ 2023-01-01 đến 2023-01-31) bằng cờ `--dry-run`:

```bash
finsight market backfill --symbols BTCUSDT,ETHUSDT --intervals 15m,1h --start 2023-01-01 --end 2023-01-31 --mode hybrid --dry-run
```

Để **thực sự tiến hành tải dữ liệu**, bạn cần thay cờ `--dry-run` bằng cờ `--no-dry-run`:

```bash
finsight market backfill --symbols BTCUSDT,ETHUSDT --intervals 15m,1h --start 2023-01-01 --end 2023-01-31 --mode hybrid --no-dry-run
```

**Dữ liệu tải về sẽ được tự động lưu và giải nén tại:**
👉 `data/bronze/binance/spot/klines/`

> [!WARNING]
> **Lỗi UnicodeEncodeError trên PowerShell (Windows)**
> Nếu đường dẫn thư mục dự án của bạn có chứa tiếng Việt có dấu (ví dụ: `D:\Tự học\AI\...`), terminal PowerShell có thể bị crash khi cố in đường dẫn file ra màn hình. Mặc dù dữ liệu vẫn được tải thành công, nhưng để tránh bị văng lỗi đỏ, bạn hãy chạy lệnh sau để ép PowerShell dùng UTF-8 trước khi gọi `finsight`:
> ```powershell
> $env:PYTHONIOENCODING="utf-8"
> ```

## Chạy bộ kiểm thử (Tests)

Nhờ việc bạn đã setup cài đặt project trực tiếp qua `pip install -e .[dev]`, mã nguồn đã tự liên kết, bạn không cần phải truyền biến `PYTHONPATH` nữa. Chỉ cần gõ:

```bash
pytest
```

## Cấu trúc Mã nguồn

- Xem chi tiết bố cục thư mục dựa theo tài liệu thiết kế tại: `docs/code_structure.md`
- Xem giải thích chi tiết chức năng của từng file và luồng phụ thuộc tại: `docs/quant_expert_file_map.md`
- Hướng dẫn cách đọc hiểu code: `docs/how_to_read_quant_expert_code.md`
- Tài liệu về Kiến trúc đa chuyên gia (Multi-expert architecture): `docs/multi_expert_architecture.md`
