# Quant Expert File Map

TÃƒÂ i liÃ¡Â»â€¡u nÃƒÂ y giÃ¡ÂºÂ£i thÃƒÂ­ch repo theo cÃ¡ÂºÂ¥u trÃƒÂºc mÃ¡Â»â€ºi, Ã„â€˜Ã†Â¡n giÃ¡ÂºÂ£n hÃ†Â¡n. HÃƒÂ£y nhÃ¡Â»â€º 6 nhÃƒÂ³m chÃƒÂ­nh:

```text
cli      = nÃ†Â¡i chÃ¡ÂºÂ¡y lÃ¡Â»â€¡nh
config   = cÃ¡ÂºÂ¥u hÃƒÂ¬nh vÃƒÂ  constant
crawl    = lÃ¡ÂºÂ¥y dÃ¡Â»Â¯ liÃ¡Â»â€¡u tÃ¡Â»Â« Binance, verify, parse, validate
database = lÃ†Â°u dÃ¡Â»Â¯ liÃ¡Â»â€¡u ra file/db
domain   = object chung nhÃ†Â° Candle
quant    = nÃ†Â¡i lÃƒÂ m feature/model Ã¡Â»Å¸ Phase 3
```

## 1. LuÃ¡Â»â€œng Build Universe

Universe lÃƒÂ  danh sÃƒÂ¡ch coin hÃ¡Â»â€¡ thÃ¡Â»â€˜ng sÃ¡ÂºÂ½ theo dÃƒÂµi.

Command:

```powershell
$env:PYTHONPATH='src'
python -m finsight.cli universe build --quote-asset USDT --limit 10
```

File chÃ¡ÂºÂ¡y theo thÃ¡Â»Â© tÃ¡Â»Â±:

```text
src/finsight/cli/universe.py
  nhÃ¡ÂºÂ­n lÃ¡Â»â€¡nh tÃ¡Â»Â« terminal
  Ã¢â€ â€œ
src/finsight/config/settings.py
  Ã„â€˜Ã¡Â»Âc cÃ¡ÂºÂ¥u hÃƒÂ¬nh nhÃ†Â° min quote volume
  Ã¢â€ â€œ
src/finsight/crawl/binance/rest_client.py
  gÃ¡Â»Âi Binance exchangeInfo vÃƒÂ  ticker/24hr
  Ã¢â€ â€œ
src/finsight/crawl/binance/schemas.py
  parse dÃ¡Â»Â¯ liÃ¡Â»â€¡u Binance vÃ¡Â»Â kiÃ¡Â»Æ’u rÃƒÂµ rÃƒÂ ng
  Ã¢â€ â€œ
src/finsight/crawl/universe_builder.py
  chÃ¡Â»Ân BTC/ETH, candidate, loÃ¡ÂºÂ¡i stablecoin/leveraged/volume thÃ¡ÂºÂ¥p
  Ã¢â€ â€œ
src/finsight/crawl/universe_report.py
  ghi report JSON
  Ã¢â€ â€œ
data/gold/universe/*.json
```

## 2. LuÃ¡Â»â€œng Download Market History ZIP

Market lÃƒÂ  dÃ¡Â»Â¯ liÃ¡Â»â€¡u giÃƒÂ¡/candle/volume cÃ¡Â»Â§a cÃƒÂ¡c coin.

Dry-run:

```powershell
$env:PYTHONPATH='src'
python -m finsight.cli market backfill --symbols BTCUSDT,ETHUSDT --intervals 15m --start 2026-01-01 --end 2026-01-31 --mode monthly-zip --dry-run
```

TÃ¡ÂºÂ£i thÃ¡ÂºÂ­t:

```powershell
$env:PYTHONPATH='src'
python -m finsight.cli market backfill --symbols BTCUSDT,ETHUSDT --intervals 15m --start 2026-01-01 --end 2026-01-31 --mode monthly-zip --no-dry-run
```

File chÃ¡ÂºÂ¡y theo thÃ¡Â»Â© tÃ¡Â»Â±:

```text
src/finsight/cli/market.py
  nhÃ¡ÂºÂ­n symbols, intervals, start, end, mode
  Ã¢â€ â€œ
src/finsight/crawl/backfill_plan.py
  tÃ¡ÂºÂ¡o BackfillRequest vÃƒÂ  BackfillPlan
  Ã¢â€ â€œ
src/finsight/crawl/service.py
  Ã„â€˜iÃ¡Â»Âu phÃ¡Â»â€˜i workflow
  Ã¢â€ â€œ
src/finsight/crawl/binance/public_data_client.py
  sinh URL Binance Public Data ZIP
  Ã¢â€ â€œ
src/finsight/crawl/downloader.py
  tÃ¡ÂºÂ£i ZIP + CHECKSUM, verify SHA-256, unzip an toÃƒÂ n
  Ã¢â€ â€œ
src/finsight/database/storage.py
  ghi metadata bronze
  Ã¢â€ â€œ
data/bronze/binance/spot/klines/...
```

## 3. GiÃ¡ÂºÂ£i ThÃƒÂ­ch TÃ¡Â»Â«ng NhÃƒÂ³m File

### cli

`src/finsight/cli/main.py`

- GÃ¡ÂºÂ¯n command `universe` vÃƒÂ  `market`.
- Khi chÃ¡ÂºÂ¡y `python -m finsight.cli ...`, file nÃƒÂ y lÃƒÂ  cÃ¡Â»Â­a vÃƒÂ o chÃƒÂ­nh.

`src/finsight/cli/universe.py`

- Command chÃ¡Â»Ân danh sÃƒÂ¡ch coin.
- GÃ¡Â»Âi Binance REST client.
- GÃ¡Â»Âi UniverseBuilder.
- Ghi universe report nÃ¡ÂºÂ¿u khÃƒÂ´ng dry-run.

`src/finsight/cli/market.py`

- Command lÃ¡ÂºÂ¥y dÃ¡Â»Â¯ liÃ¡Â»â€¡u market.
- TÃ¡ÂºÂ¡o BackfillRequest.
- GÃ¡Â»Âi HistoricalIngestionService.
- NÃ¡ÂºÂ¿u `--dry-run`, chÃ¡Â»â€° in URL.
- NÃ¡ÂºÂ¿u `--no-dry-run`, tÃ¡ÂºÂ£i dÃ¡Â»Â¯ liÃ¡Â»â€¡u thÃ¡ÂºÂ­t.

### config

`src/finsight/config/settings.py`

- Ã„ÂÃ¡Â»Âc biÃ¡ÂºÂ¿n mÃƒÂ´i trÃ†Â°Ã¡Â»Âng tÃ¡Â»Â« `.env`.
- VÃƒÂ­ dÃ¡Â»Â¥: Binance base URL, min quote volume.

`src/finsight/config/constants.py`

- Constant cÃ¡ÂºÂ¥p sÃ¡ÂºÂ£n phÃ¡ÂºÂ©m.
- ChÃ¡Â»Â©a required symbols, candidate symbols, interval, stablecoin list.

`src/finsight/config/crawl_constants.py`

- Constant riÃƒÂªng cho crawl.
- ChÃ¡Â»Â©a `BackfillMode`, `IngestionSource`, default path, limit, filename.

`src/finsight/config/crawl_config.py`

- Config object cho crawl.
- Downloader, REST backfill, storage nhÃ¡ÂºÂ­n config tÃ¡Â»Â« Ã„â€˜ÃƒÂ¢y.

### crawl

`src/finsight/crawl/base.py`

- Interface chung cho market data provider.

`src/finsight/crawl/universe_builder.py`

- Business logic chÃ¡Â»Ân universe.
- KhÃƒÂ´ng tÃ¡ÂºÂ£i candle.
- ChÃ¡Â»â€° quyÃ¡ÂºÂ¿t Ã„â€˜Ã¡Â»â€¹nh coin nÃƒÂ o hÃ¡Â»Â£p lÃ¡Â»â€¡ Ã„â€˜Ã¡Â»Æ’ phÃƒÂ¢n tÃƒÂ­ch.

`src/finsight/crawl/universe_report.py`

- Ghi kÃ¡ÂºÂ¿t quÃ¡ÂºÂ£ universe ra JSON.

`src/finsight/crawl/backfill_plan.py`

- TÃƒÂ­nh xem cÃ¡ÂºÂ§n tÃ¡ÂºÂ£i file nÃƒÂ o.
- KhÃƒÂ´ng download.
- VÃƒÂ­ dÃ¡Â»Â¥ tÃ¡Â»Â« Jan Ã„â€˜Ã¡ÂºÂ¿n Mar sÃ¡ÂºÂ½ sinh 3 monthly ZIP cho mÃ¡Â»â€”i symbol/interval.

`src/finsight/crawl/downloader.py`

- Code download thÃ¡ÂºÂ­t.
- CÃƒÂ³ `BulkDownloader`, `ChecksumVerifier`, `SafeZipExtractor`.

`src/finsight/crawl/rest_backfill.py`

- LÃ¡ÂºÂ¥y dÃ¡Â»Â¯ liÃ¡Â»â€¡u qua REST `/api/v3/klines`.
- DÃƒÂ¹ng cho incremental backfill sau monthly ZIP.

`src/finsight/crawl/validator.py`

- KiÃ¡Â»Æ’m tra candle: duplicate, missing, OHLC sai, volume ÃƒÂ¢m, timestamp lÃ¡Â»â€”i.

`src/finsight/crawl/service.py`

- File Ã„â€˜iÃ¡Â»Âu phÃ¡Â»â€˜i chÃƒÂ­nh.
- CLI gÃ¡Â»Âi service, service gÃ¡Â»Âi planner/downloader/storage.

### crawl/binance

`src/finsight/crawl/binance/rest_client.py`

- GÃ¡Â»Âi Binance REST public API.

`src/finsight/crawl/binance/public_data_client.py`

- Sinh URL file ZIP/CHECKSUM tÃ¡Â»Â« `data.binance.vision`.

`src/finsight/crawl/binance/schemas.py`

- Parse response Binance `exchangeInfo`, `ticker/24hr`.

`src/finsight/crawl/binance/normalizer.py`

- ChuyÃ¡Â»Æ’n row kline Binance thÃƒÂ nh object `Candle`.

`src/finsight/crawl/binance/timestamp_parser.py`

- TÃ¡Â»Â± nhÃ¡ÂºÂ­n timestamp milliseconds hoÃ¡ÂºÂ·c microseconds.

### database

`src/finsight/database/storage.py`

- Ghi dÃ¡Â»Â¯ liÃ¡Â»â€¡u ra disk.
- HiÃ¡Â»â€¡n cÃƒÂ³:
  - `BronzeMetadataWriter`
  - `SilverCandleWriter`

Sau nÃƒÂ y nÃ¡ÂºÂ¿u thÃƒÂªm PostgreSQL thÃƒÂ¬ database models/repository cÃ…Â©ng Ã„â€˜Ã¡Â»Æ’ Ã¡Â»Å¸ Ã„â€˜ÃƒÂ¢y.

### domain

`src/finsight/domain/entities.py`

- ChÃ¡Â»Â©a `Candle` chuÃ¡ÂºÂ©n nÃ¡Â»â„¢i bÃ¡Â»â„¢.
- Quant sau nÃƒÂ y nÃƒÂªn dÃƒÂ¹ng `Candle`, khÃƒÂ´ng dÃƒÂ¹ng Binance raw row trÃ¡Â»Â±c tiÃ¡ÂºÂ¿p.

`src/finsight/domain/enums.py`

- Enum chung.

`src/finsight/domain/events.py`

- Event chung, dÃƒÂ¹ng cho realtime sau nÃƒÂ y.

`src/finsight/domain/schemas.py`

- Schema chung.

### quant

`src/finsight/experts/quant/README.md`

- Ã„ÂÃƒÂ¡nh dÃ¡ÂºÂ¥u nÃ†Â¡i lÃƒÂ m Phase 3.
- ChÃ†Â°a cÃƒÂ³ logic thÃ¡ÂºÂ­t.

## 4. SÃ¡Â»Â­a File NÃƒÂ o Khi MuÃ¡Â»â€˜n LÃƒÂ m ViÃ¡Â»â€¡c GÃƒÂ¬

Ã„ÂÃ¡Â»â€¢i cÃ¡ÂºÂ¥u hÃƒÂ¬nh symbol/interval/stablecoin:

```text
src/finsight/config/constants.py
```

Ã„ÂÃ¡Â»â€¢i cÃ¡ÂºÂ¥u hÃƒÂ¬nh crawl path/limit/source:

```text
src/finsight/config/crawl_constants.py
src/finsight/config/crawl_config.py
```

Ã„ÂÃ¡Â»â€¢i cÃƒÂ¡ch chÃ¡Â»Ân coin:

```text
src/finsight/crawl/universe_builder.py
```

Ã„ÂÃ¡Â»â€¢i cÃƒÂ¡ch tÃ¡ÂºÂ¡o URL Binance ZIP:

```text
src/finsight/crawl/binance/public_data_client.py
```

Ã„ÂÃ¡Â»â€¢i cÃƒÂ¡ch download/checksum/unzip:

```text
src/finsight/crawl/downloader.py
```

Ã„ÂÃ¡Â»â€¢i cÃƒÂ¡ch lÃ¡ÂºÂ¥y REST kline:

```text
src/finsight/crawl/rest_backfill.py
```

Ã„ÂÃ¡Â»â€¢i cÃƒÂ¡ch lÃ†Â°u file:

```text
src/finsight/database/storage.py
```

Ã„ÂÃ¡Â»â€¢i command terminal:

```text
src/finsight/cli/universe.py
src/finsight/cli/market.py
```

LÃƒÂ m Quant Phase 3:

```text
src/finsight/experts/quant/
```

## 5. VÃƒÂ¬ Sao Chia NhÃ†Â° VÃ¡ÂºÂ­y

KhÃƒÂ´ng Ã„â€˜Ã¡Â»Æ’ tÃ¡ÂºÂ¥t cÃ¡ÂºÂ£ trong mÃ¡Â»â„¢t folder vÃƒÂ¬ sÃ¡ÂºÂ½ rÃ¡Â»â€˜i. NhÃ†Â°ng cÃ…Â©ng khÃƒÂ´ng chia quÃƒÂ¡ sÃƒÂ¢u theo kiÃ¡Â»Æ’u enterprise.

CÃƒÂ¡ch hiÃ¡Â»â€¡n tÃ¡ÂºÂ¡i:

```text
config   quÃ¡ÂºÂ£n cÃ¡ÂºÂ¥u hÃƒÂ¬nh
crawl    lÃ¡ÂºÂ¥y vÃƒÂ  xÃ¡Â»Â­ lÃƒÂ½ dÃ¡Â»Â¯ liÃ¡Â»â€¡u nguÃ¡Â»â€œn
database lÃ†Â°u dÃ¡Â»Â¯ liÃ¡Â»â€¡u
domain   Ã„â€˜Ã¡Â»â€¹nh nghÃ„Â©a object chung
cli      cÃ¡Â»Â­a vÃƒÂ o chÃ¡ÂºÂ¡y lÃ¡Â»â€¡nh
quant    model/feature sau nÃƒÂ y
```

Ã„ÂÃƒÂ¢y lÃƒÂ  mÃ¡Â»Â©c chia vÃ¡Â»Â«a Ã„â€˜Ã¡Â»Â§ cho bÃ¡ÂºÂ¡n Ã„â€˜Ã¡Â»Âc, sÃ¡Â»Â­a vÃƒÂ  mÃ¡Â»Å¸ rÃ¡Â»â„¢ng.