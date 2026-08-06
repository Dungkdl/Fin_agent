# Hướng Dẫn Đọc Code Quant Expert

Tài liệu này giúp bạn đọc repo theo đúng luồng, không bị lạc giữa nhiều file.

## 1. Cấu Trúc Đơn Giản Hiện Tại

```text
src/finsight/
├── cli/        # nơi nhận lệnh terminal
├── config/     # cấu hình, constant, setting
├── crawl/      # code lấy dữ liệu Binance và xử lý dữ liệu thô
├── database/   # code lưu dữ liệu
├── domain/     # object chung như Candle
└── experts/quant/      # nơi làm Quant Expert Phase 3
```

Bạn chỉ cần nhớ:

```text
cli gọi crawl service
crawl lấy dữ liệu
crawl/binance biết Binance cụ thể
crawl xử lý/validate
database lưu dữ liệu
domain là object chung
quant dùng dữ liệu đã chuẩn hóa để build feature/model
```

## 2. Thứ Tự Đọc File Nên Theo

### Bước 1: Đọc lệnh người dùng chạy

Đọc trước:

```text
src/finsight/cli/main.py
src/finsight/cli/universe.py
src/finsight/cli/market.py
```

Lý do: đây là cửa vào. Bạn sẽ biết user chạy command nào và command đó gọi xuống đâu.

### Bước 2: Đọc service điều phối

```text
src/finsight/crawl/service.py
```

Đây là file quan trọng nhất để hiểu workflow crawl. Nó nối:

```text
BackfillPlan
BulkDownloader
SafeZipExtractor
BronzeMetadataWriter
```

### Bước 3: Đọc phần lập kế hoạch tải

```text
src/finsight/crawl/backfill_plan.py
```

File này trả lời câu hỏi:

```text
Với BTCUSDT, 15m, từ 2026-01 đến 2026-03 thì cần tải những ZIP nào?
```

### Bước 4: Đọc phần Binance cụ thể

```text
src/finsight/crawl/binance/public_data_client.py
src/finsight/crawl/binance/rest_client.py
src/finsight/crawl/binance/schemas.py
src/finsight/crawl/binance/normalizer.py
src/finsight/crawl/binance/timestamp_parser.py
```

Nhóm này trả lời:

```text
Binance URL nằm ở đâu?
REST endpoint gọi thế nào?
Dữ liệu Binance parse ra sao?
Timestamp ms/microseconds xử lý thế nào?
```

### Bước 5: Đọc phần download và kiểm tra dữ liệu

```text
src/finsight/crawl/downloader.py
src/finsight/crawl/validator.py
```

`downloader.py` tải ZIP, tải CHECKSUM, verify rồi unzip.

`validator.py` kiểm tra candle có lỗi không.

### Bước 6: Đọc phần lưu dữ liệu

```text
src/finsight/database/storage.py
```

File này ghi:

```text
bronze metadata
silver parquet
```

### Bước 7: Đọc object chung

```text
src/finsight/domain/entities.py
```

Quan trọng nhất là `Candle`. Đây là object chuẩn để Quant dùng sau này.

## 3. Luồng Universe

Universe = chọn coin nào để phân tích.

Command:

```powershell
$env:PYTHONPATH='src'
python -m finsight.cli universe build --quote-asset USDT --limit 10
```

Luồng file:

```text
cli/universe.py
  ↓
config/settings.py
  ↓
crawl/binance/rest_client.py
  ↓
crawl/binance/schemas.py
  ↓
crawl/universe_builder.py
  ↓
crawl/universe_report.py
  ↓
data/gold/universe/*.json
```

## 4. Luồng Market History ZIP

Market = dữ liệu giá/candle/volume.

Dry-run:

```powershell
$env:PYTHONPATH='src'
python -m finsight.cli market backfill --symbols BTCUSDT,ETHUSDT --intervals 15m --start 2026-01-01 --end 2026-01-31 --mode monthly-zip --dry-run
```

Tải thật:

```powershell
$env:PYTHONPATH='src'
python -m finsight.cli market backfill --symbols BTCUSDT,ETHUSDT --intervals 15m --start 2026-01-01 --end 2026-01-31 --mode monthly-zip --no-dry-run
```

Luồng file:

```text
cli/market.py
  ↓
crawl/backfill_plan.py
  ↓
crawl/service.py
  ↓
crawl/binance/public_data_client.py
  ↓
crawl/downloader.py
  ↓
database/storage.py
  ↓
data/bronze/binance/spot/klines/...
```

## 5. File Nào Sửa Khi Muốn Làm Gì

Đổi symbol mặc định, interval, stablecoin list:

```text
src/finsight/config/constants.py
```

Đổi path lưu data, REST limit, filename:

```text
src/finsight/config/crawl_constants.py
src/finsight/config/crawl_config.py
```

Đổi rule chọn universe:

```text
src/finsight/crawl/universe_builder.py
```

Đổi cách tạo URL ZIP:

```text
src/finsight/crawl/binance/public_data_client.py
```

Đổi cách gọi Binance REST:

```text
src/finsight/crawl/binance/rest_client.py
```

Đổi cách download/checksum/unzip:

```text
src/finsight/crawl/downloader.py
```

Đổi cách validate candle:

```text
src/finsight/crawl/validator.py
```

Đổi cách lưu bronze/silver:

```text
src/finsight/database/storage.py
```

Bắt đầu làm Quant feature/model:

```text
src/finsight/experts/quant/
```

## 6. Cách Hiểu Trách Nhiệm Từng Tầng

```text
cli
  chỉ nhận lệnh và in kết quả

config
  chứa cấu hình, không crawl, không train

crawl
  lấy dữ liệu, parse, verify, validate

database
  ghi/lưu dữ liệu

domain
  định nghĩa object chung

quant
  dùng dữ liệu đã chuẩn hóa để tạo feature, label, train model
```

Nếu một file làm sai trách nhiệm, ví dụ `cli` tự download hoặc `quant` tự gọi Binance raw ZIP, thì sau này code sẽ rối.
