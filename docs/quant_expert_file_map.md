# Bản Đồ File Quant Expert

Tài liệu này giải thích repo theo cấu trúc mới, đơn giản hơn. Hãy nhớ 6 nhóm chính:

```text
cli      = nơi chạy lệnh
config   = cấu hình và constant
crawl    = lấy dữ liệu từ Binance, verify, parse, validate
database = lưu dữ liệu ra file/db
domain   = object chung như Candle
quant    = nơi làm feature/model ở Phase 3
```

## 1. Luồng Build Universe

Universe là danh sách coin hợp lệ mà hệ thống sẽ theo dõi.

Command:

```powershell
$env:PYTHONPATH='src'
python -m finsight.cli universe build --quote-asset USDT --limit 10
```

Luồng file:

```text
src/finsight/cli/universe.py
  nhận lệnh từ terminal
  ↓
src/finsight/config/settings.py
  đọc cấu hình như min quote volume
  ↓
src/finsight/crawl/binance/rest_client.py
  gọi Binance exchangeInfo và ticker/24hr
  ↓
src/finsight/crawl/binance/schemas.py
  parse dữ liệu Binance về kiểu rõ ràng
  ↓
src/finsight/crawl/universe_builder.py
  chọn BTC/ETH, candidate, loại stablecoin/leveraged/volume thấp
  ↓
src/finsight/crawl/universe_report.py
  ghi report JSON
  ↓
data/gold/universe/*.json
```

## 2. Luồng Download Market History ZIP

Market là dữ liệu giá/candle/volume của các coin.

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
src/finsight/cli/market.py
  nhận symbols, intervals, start, end, mode
  ↓
src/finsight/crawl/backfill_plan.py
  tạo BackfillRequest và BackfillPlan
  ↓
src/finsight/crawl/service.py
  điều phối workflow
  ↓
src/finsight/crawl/binance/public_data_client.py
  sinh URL Binance Public Data ZIP
  ↓
src/finsight/crawl/downloader.py
  tải ZIP + CHECKSUM, verify SHA-256, unzip an toàn
  ↓
src/finsight/database/storage.py
  ghi metadata bronze
  ↓
data/bronze/binance/spot/klines/...
```

## 3. Giải Thích Từng Nhóm File

### cli

`src/finsight/cli/main.py`

- Gắn command `universe` và `market`.
- Khi chạy `python -m finsight.cli ...`, file này là cửa vào chính.

`src/finsight/cli/universe.py`

- Command chọn danh sách coin.
- Gọi Binance REST client.
- Gọi UniverseBuilder.
- Ghi universe report nếu không dry-run.

`src/finsight/cli/market.py`

- Command lấy dữ liệu market.
- Tạo BackfillRequest.
- Gọi HistoricalIngestionService.
- Nếu `--dry-run`, chỉ in URL.
- Nếu `--no-dry-run`, tải dữ liệu thật.

### config

`src/finsight/config/settings.py`

- Đọc biến môi trường từ `.env`.
- Ví dụ: Binance base URL, min quote volume.

`src/finsight/config/constants.py`

- Constant cấp sản phẩm.
- Chứa required symbols, candidate symbols, interval, stablecoin list.

`src/finsight/config/crawl_constants.py`

- Constant riêng cho crawl.
- Chứa `BackfillMode`, `IngestionSource`, default path, limit, filename.

`src/finsight/config/crawl_config.py`

- Config object cho crawl.
- Downloader, REST backfill, storage nhận config từ đây.

### crawl

`src/finsight/crawl/base.py`

- Interface chung cho market data provider.

`src/finsight/crawl/universe_builder.py`

- Business logic chọn universe.
- Không tải candle.
- Chỉ quyết định coin nào hợp lệ để phân tích.

`src/finsight/crawl/universe_report.py`

- Ghi kết quả universe ra JSON.

`src/finsight/crawl/backfill_plan.py`

- Tính xem cần tải file nào.
- Không download.
- Ví dụ từ Jan đến Mar sẽ sinh 3 monthly ZIP cho mỗi symbol/interval.

`src/finsight/crawl/downloader.py`

- Code download thật.
- Có `BulkDownloader`, `ChecksumVerifier`, `SafeZipExtractor`.

`src/finsight/crawl/rest_backfill.py`

- Lấy dữ liệu qua REST `/api/v3/klines`.
- Dùng cho incremental backfill sau monthly ZIP.

`src/finsight/crawl/validator.py`

- Kiểm tra candle: duplicate, missing, OHLC sai, volume âm, timestamp lỗi.

`src/finsight/crawl/service.py`

- File điều phối chính.
- CLI gọi service, service gọi planner/downloader/storage.

### crawl/binance

`src/finsight/crawl/binance/rest_client.py`

- Gọi Binance REST public API.

`src/finsight/crawl/binance/public_data_client.py`

- Sinh URL file ZIP/CHECKSUM từ `data.binance.vision`.

`src/finsight/crawl/binance/schemas.py`

- Parse response Binance `exchangeInfo`, `ticker/24hr`.

`src/finsight/crawl/binance/normalizer.py`

- Chuyển row kline Binance thành object `Candle`.

`src/finsight/crawl/binance/timestamp_parser.py`

- Tự nhận timestamp milliseconds hoặc microseconds.

### database

`src/finsight/database/storage.py`

- Ghi dữ liệu ra disk.
- Hiện có:
  - `BronzeMetadataWriter`
  - `SilverCandleWriter`

Sau này nếu thêm PostgreSQL thì database models/repository cũng để ở đây.

### domain

`src/finsight/domain/entities.py`

- Chứa `Candle` chuẩn nội bộ.
- Quant sau này nên dùng `Candle`, không dùng Binance raw row trực tiếp.

`src/finsight/domain/enums.py`

- Enum chung.

`src/finsight/domain/events.py`

- Event chung, dùng cho realtime sau này.

`src/finsight/domain/schemas.py`

- Schema chung.

### quant

`src/finsight/experts/quant/README.md`

- Đánh dấu nơi làm Phase 3.
- Chưa có logic thật.

## 4. Sửa File Nào Khi Muốn Làm Việc Gì

Đổi cấu hình symbol/interval/stablecoin:

```text
src/finsight/config/constants.py
```

Đổi cấu hình crawl path/limit/source:

```text
src/finsight/config/crawl_constants.py
src/finsight/config/crawl_config.py
```

Đổi cách chọn coin:

```text
src/finsight/crawl/universe_builder.py
```

Đổi cách tạo URL Binance ZIP:

```text
src/finsight/crawl/binance/public_data_client.py
```

Đổi cách download/checksum/unzip:

```text
src/finsight/crawl/downloader.py
```

Đổi cách lấy REST kline:

```text
src/finsight/crawl/rest_backfill.py
```

Đổi cách lưu file:

```text
src/finsight/database/storage.py
```

Đổi command terminal:

```text
src/finsight/cli/universe.py
src/finsight/cli/market.py
```

Làm Quant Phase 3:

```text
src/finsight/experts/quant/
```

## 5. Vì Sao Chia Như Vậy

Không để tất cả trong một folder vì sẽ rối. Nhưng cũng không chia quá sâu theo kiểu enterprise.

Cách hiện tại:

```text
config   quản cấu hình
crawl    lấy và xử lý dữ liệu nguồn
database lưu dữ liệu
domain   định nghĩa object chung
cli      cửa vào chạy lệnh
quant    model/feature sau này
```

Đây là mức chia vừa đủ cho bạn đọc, sửa và mở rộng.
