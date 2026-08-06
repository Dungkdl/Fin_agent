# Cấu Trúc Mã Nguồn

Repo đã được sắp xếp lại theo hướng đơn giản, dễ đọc, để nhấn mạnh trách nhiệm chính của từng thư mục.

```text
src/finsight/
├── cli/        # nơi nhận lệnh từ terminal người dùng
├── config/     # settings, constants, config object
├── crawl/      # code lấy dữ liệu từ Binance và xử lý ingestion
│   └── binance/ # code riêng cho Binance
├── database/   # code ghi/lưu dữ liệu
├── domain/     # object/schema nghiệp vụ dùng chung
└── experts/quant/      # Phase 3: feature, label, dataset, model
```

## Nhóm Chính

### cli

Chỉ nhận input từ terminal rồi gọi service. Không để business logic lớn ở đây.

- `cli/main.py`: đăng ký command group.
- `cli/universe.py`: command build universe.
- `cli/market.py`: command backfill dữ liệu market.

### config

Chứa cấu hình và constant dùng chung.

- `settings.py`: đọc env bằng pydantic-settings.
- `constants.py`: symbol, interval, stablecoin, model task.
- `crawl_constants.py`: mode crawl, source type, default path, limit.
- `crawl_config.py`: config object cho downloader/backfill/storage.
- `time.py`: helper UTC.
- `logging.py`: logging setup.
- `exceptions.py`: exception chung.

### crawl

Chứa toàn bộ code lấy dữ liệu và xử lý ingestion.

- `universe_builder.py`: chọn danh sách coin hợp lệ.
- `universe_report.py`: ghi report universe.
- `backfill_plan.py`: lập kế hoạch cần tải file nào.
- `downloader.py`: tải ZIP/CHECKSUM, verify SHA-256, giải nén an toàn.
- `rest_backfill.py`: lấy dữ liệu qua REST `/api/v3/klines`.
- `validator.py`: kiểm tra chất lượng candle.
- `service.py`: nối planner, downloader, extractor, metadata writer.
- `binance/`: code cụ thể cho Binance.

### database

Chứa code lưu dữ liệu.

- `storage.py`: ghi bronze metadata và silver parquet.

Sau này nếu thêm PostgreSQL/Alembic thì cũng để trong `database/`.

### domain

Chứa object chung, không phụ thuộc Binance.

- `entities.py`: `Candle`.
- `enums.py`: enum asset/exchange/trading mode.
- `events.py`: event nghiệp vụ.
- `schemas.py`: schema dùng chung.

### quant

Chưa triển khai logic. Phase 3 sẽ viết ở đây theo dạng đơn giản:

- `features.py`
- `labels.py`
- `dataset.py`
- `models.py`
- `train.py`
- `predict.py`

## Luồng Hiện Tại

Build universe:

```text
cli/universe.py
  ↓
crawl/binance/rest_client.py
  ↓
crawl/universe_builder.py
  ↓
crawl/universe_report.py
  ↓
data/gold/universe/*.json
```

Download market ZIP:

```text
cli/market.py
  ↓
crawl/service.py
  ↓
crawl/backfill_plan.py
  ↓
crawl/binance/public_data_client.py
  ↓
crawl/downloader.py
  ↓
database/storage.py
  ↓
data/bronze/binance/spot/klines/...
```