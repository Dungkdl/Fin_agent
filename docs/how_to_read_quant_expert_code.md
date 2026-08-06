# HÃ†Â°Ã¡Â»â€ºng DÃ¡ÂºÂ«n Ã„ÂÃ¡Â»Âc Code Quant Expert

TÃƒÂ i liÃ¡Â»â€¡u nÃƒÂ y giÃƒÂºp bÃ¡ÂºÂ¡n Ã„â€˜Ã¡Â»Âc repo theo Ã„â€˜ÃƒÂºng luÃ¡Â»â€œng, khÃƒÂ´ng bÃ¡Â»â€¹ lÃ¡ÂºÂ¡c giÃ¡Â»Â¯a nhiÃ¡Â»Âu file.

## 1. CÃ¡ÂºÂ¥u TrÃƒÂºc Ã„ÂÃ†Â¡n GiÃ¡ÂºÂ£n HiÃ¡Â»â€¡n TÃ¡ÂºÂ¡i

```text
src/finsight/
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ cli/        # nÃ†Â¡i nhÃ¡ÂºÂ­n lÃ¡Â»â€¡nh terminal
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ config/     # cÃ¡ÂºÂ¥u hÃƒÂ¬nh, constant, setting
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ crawl/      # code lÃ¡ÂºÂ¥y dÃ¡Â»Â¯ liÃ¡Â»â€¡u Binance vÃƒÂ  xÃ¡Â»Â­ lÃƒÂ½ dÃ¡Â»Â¯ liÃ¡Â»â€¡u thÃƒÂ´
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ database/   # code lÃ†Â°u dÃ¡Â»Â¯ liÃ¡Â»â€¡u
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ domain/     # object chung nhÃ†Â° Candle
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ experts/quant/      # nÃ†Â¡i lÃƒÂ m Quant Expert Phase 3
```

BÃ¡ÂºÂ¡n chÃ¡Â»â€° cÃ¡ÂºÂ§n nhÃ¡Â»â€º:

```text
cli gÃ¡Â»Âi crawl service
crawl lÃ¡ÂºÂ¥y dÃ¡Â»Â¯ liÃ¡Â»â€¡u
crawl/binance biÃ¡ÂºÂ¿t Binance cÃ¡Â»Â¥ thÃ¡Â»Æ’
crawl xÃ¡Â»Â­ lÃƒÂ½/validate
 database lÃ†Â°u dÃ¡Â»Â¯ liÃ¡Â»â€¡u
domain lÃƒÂ  object chung
quant dÃƒÂ¹ng dÃ¡Â»Â¯ liÃ¡Â»â€¡u Ã„â€˜ÃƒÂ£ chuÃ¡ÂºÂ©n hÃƒÂ³a Ã„â€˜Ã¡Â»Æ’ build feature/model
```

## 2. ThÃ¡Â»Â© TÃ¡Â»Â± Ã„ÂÃ¡Â»Âc File NÃƒÂªn Theo

### BÃ†Â°Ã¡Â»â€ºc 1: Ã„ÂÃ¡Â»Âc lÃ¡Â»â€¡nh ngÃ†Â°Ã¡Â»Âi dÃƒÂ¹ng chÃ¡ÂºÂ¡y

Ã„ÂÃ¡Â»Âc trÃ†Â°Ã¡Â»â€ºc:

```text
src/finsight/cli/main.py
src/finsight/cli/universe.py
src/finsight/cli/market.py
```

LÃƒÂ½ do: Ã„â€˜ÃƒÂ¢y lÃƒÂ  cÃ¡Â»Â­a vÃƒÂ o. BÃ¡ÂºÂ¡n sÃ¡ÂºÂ½ biÃ¡ÂºÂ¿t user chÃ¡ÂºÂ¡y command nÃƒÂ o vÃƒÂ  command Ã„â€˜ÃƒÂ³ gÃ¡Â»Âi xuÃ¡Â»â€˜ng Ã„â€˜ÃƒÂ¢u.

### BÃ†Â°Ã¡Â»â€ºc 2: Ã„ÂÃ¡Â»Âc service Ã„â€˜iÃ¡Â»Âu phÃ¡Â»â€˜i

```text
src/finsight/crawl/service.py
```

Ã„ÂÃƒÂ¢y lÃƒÂ  file quan trÃ¡Â»Âng nhÃ¡ÂºÂ¥t Ã„â€˜Ã¡Â»Æ’ hiÃ¡Â»Æ’u workflow crawl. NÃƒÂ³ nÃ¡Â»â€˜i:

```text
BackfillPlan
BulkDownloader
SafeZipExtractor
BronzeMetadataWriter
```

### BÃ†Â°Ã¡Â»â€ºc 3: Ã„ÂÃ¡Â»Âc phÃ¡ÂºÂ§n lÃ¡ÂºÂ­p kÃ¡ÂºÂ¿ hoÃ¡ÂºÂ¡ch tÃ¡ÂºÂ£i

```text
src/finsight/crawl/backfill_plan.py
```

File nÃƒÂ y trÃ¡ÂºÂ£ lÃ¡Â»Âi cÃƒÂ¢u hÃ¡Â»Âi:

```text
VÃ¡Â»â€ºi BTCUSDT, 15m, tÃ¡Â»Â« 2026-01 Ã„â€˜Ã¡ÂºÂ¿n 2026-03 thÃƒÂ¬ cÃ¡ÂºÂ§n tÃ¡ÂºÂ£i nhÃ¡Â»Â¯ng ZIP nÃƒÂ o?
```

### BÃ†Â°Ã¡Â»â€ºc 4: Ã„ÂÃ¡Â»Âc phÃ¡ÂºÂ§n Binance cÃ¡Â»Â¥ thÃ¡Â»Æ’

```text
src/finsight/crawl/binance/public_data_client.py
src/finsight/crawl/binance/rest_client.py
src/finsight/crawl/binance/schemas.py
src/finsight/crawl/binance/normalizer.py
src/finsight/crawl/binance/timestamp_parser.py
```

NhÃƒÂ³m nÃƒÂ y trÃ¡ÂºÂ£ lÃ¡Â»Âi:

```text
Binance URL nÃ¡ÂºÂ±m Ã¡Â»Å¸ Ã„â€˜ÃƒÂ¢u?
REST endpoint gÃ¡Â»Âi thÃ¡ÂºÂ¿ nÃƒÂ o?
DÃ¡Â»Â¯ liÃ¡Â»â€¡u Binance parse ra sao?
Timestamp ms/microseconds xÃ¡Â»Â­ lÃƒÂ½ thÃ¡ÂºÂ¿ nÃƒÂ o?
```

### BÃ†Â°Ã¡Â»â€ºc 5: Ã„ÂÃ¡Â»Âc phÃ¡ÂºÂ§n download vÃƒÂ  kiÃ¡Â»Æ’m tra dÃ¡Â»Â¯ liÃ¡Â»â€¡u

```text
src/finsight/crawl/downloader.py
src/finsight/crawl/validator.py
```

`downloader.py` tÃ¡ÂºÂ£i ZIP, tÃ¡ÂºÂ£i CHECKSUM, verify vÃƒÂ  unzip.

`validator.py` kiÃ¡Â»Æ’m tra candle cÃƒÂ³ lÃ¡Â»â€”i khÃƒÂ´ng.

### BÃ†Â°Ã¡Â»â€ºc 6: Ã„ÂÃ¡Â»Âc phÃ¡ÂºÂ§n lÃ†Â°u dÃ¡Â»Â¯ liÃ¡Â»â€¡u

```text
src/finsight/database/storage.py
```

File nÃƒÂ y ghi:

```text
bronze metadata
silver parquet
```

### BÃ†Â°Ã¡Â»â€ºc 7: Ã„ÂÃ¡Â»Âc object chung

```text
src/finsight/domain/entities.py
```

Quan trÃ¡Â»Âng nhÃ¡ÂºÂ¥t lÃƒÂ  `Candle`. Ã„ÂÃƒÂ¢y lÃƒÂ  object chuÃ¡ÂºÂ©n Ã„â€˜Ã¡Â»Æ’ Quant dÃƒÂ¹ng sau nÃƒÂ y.

## 3. LuÃ¡Â»â€œng Universe

Universe = chÃ¡Â»Ân coin nÃƒÂ o Ã„â€˜Ã¡Â»Æ’ phÃƒÂ¢n tÃƒÂ­ch.

Command:

```powershell
$env:PYTHONPATH='src'
python -m finsight.cli universe build --quote-asset USDT --limit 10
```

LuÃ¡Â»â€œng file:

```text
cli/universe.py
  Ã¢â€ â€œ
config/settings.py
  Ã¢â€ â€œ
crawl/binance/rest_client.py
  Ã¢â€ â€œ
crawl/binance/schemas.py
  Ã¢â€ â€œ
crawl/universe_builder.py
  Ã¢â€ â€œ
crawl/universe_report.py
  Ã¢â€ â€œ
data/gold/universe/*.json
```

## 4. LuÃ¡Â»â€œng Market History ZIP

Market = dÃ¡Â»Â¯ liÃ¡Â»â€¡u giÃƒÂ¡/candle/volume.

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

LuÃ¡Â»â€œng file:

```text
cli/market.py
  Ã¢â€ â€œ
crawl/backfill_plan.py
  Ã¢â€ â€œ
crawl/service.py
  Ã¢â€ â€œ
crawl/binance/public_data_client.py
  Ã¢â€ â€œ
crawl/downloader.py
  Ã¢â€ â€œ
database/storage.py
  Ã¢â€ â€œ
data/bronze/binance/spot/klines/...
```

## 5. File NÃƒÂ o SÃ¡Â»Â­a Khi MuÃ¡Â»â€˜n LÃƒÂ m GÃƒÂ¬

Ã„ÂÃ¡Â»â€¢i symbol mÃ¡ÂºÂ·c Ã„â€˜Ã¡Â»â€¹nh, interval, stablecoin list:

```text
src/finsight/config/constants.py
```

Ã„ÂÃ¡Â»â€¢i path lÃ†Â°u data, REST limit, filename:

```text
src/finsight/config/crawl_constants.py
src/finsight/config/crawl_config.py
```

Ã„ÂÃ¡Â»â€¢i rule chÃ¡Â»Ân universe:

```text
src/finsight/crawl/universe_builder.py
```

Ã„ÂÃ¡Â»â€¢i cÃƒÂ¡ch tÃ¡ÂºÂ¡o URL ZIP:

```text
src/finsight/crawl/binance/public_data_client.py
```

Ã„ÂÃ¡Â»â€¢i cÃƒÂ¡ch gÃ¡Â»Âi Binance REST:

```text
src/finsight/crawl/binance/rest_client.py
```

Ã„ÂÃ¡Â»â€¢i cÃƒÂ¡ch download/checksum/unzip:

```text
src/finsight/crawl/downloader.py
```

Ã„ÂÃ¡Â»â€¢i cÃƒÂ¡ch validate candle:

```text
src/finsight/crawl/validator.py
```

Ã„ÂÃ¡Â»â€¢i cÃƒÂ¡ch lÃ†Â°u bronze/silver:

```text
src/finsight/database/storage.py
```

BÃ¡ÂºÂ¯t Ã„â€˜Ã¡ÂºÂ§u lÃƒÂ m Quant feature/model:

```text
src/finsight/experts/quant/
```

## 6. CÃƒÂ¡ch HiÃ¡Â»Æ’u TrÃƒÂ¡ch NhiÃ¡Â»â€¡m TÃ¡Â»Â«ng TÃ¡ÂºÂ§ng

```text
cli
  chÃ¡Â»â€° nhÃ¡ÂºÂ­n lÃ¡Â»â€¡nh vÃƒÂ  in kÃ¡ÂºÂ¿t quÃ¡ÂºÂ£

config
  chÃ¡Â»Â©a cÃ¡ÂºÂ¥u hÃƒÂ¬nh, khÃƒÂ´ng crawl, khÃƒÂ´ng train

crawl
  lÃ¡ÂºÂ¥y dÃ¡Â»Â¯ liÃ¡Â»â€¡u, parse, verify, validate

database
  ghi/lÃ†Â°u dÃ¡Â»Â¯ liÃ¡Â»â€¡u

domain
  Ã„â€˜Ã¡Â»â€¹nh nghÃ„Â©a object chung

quant
  dÃƒÂ¹ng dÃ¡Â»Â¯ liÃ¡Â»â€¡u Ã„â€˜ÃƒÂ£ chuÃ¡ÂºÂ©n hÃƒÂ³a Ã„â€˜Ã¡Â»Æ’ tÃ¡ÂºÂ¡o feature, label, train model
```

NÃ¡ÂºÂ¿u mÃ¡Â»â„¢t file lÃƒÂ m sai trÃƒÂ¡ch nhiÃ¡Â»â€¡m, vÃƒÂ­ dÃ¡Â»Â¥ `cli` tÃ¡Â»Â± download hoÃ¡ÂºÂ·c `quant` tÃ¡Â»Â± gÃ¡Â»Âi Binance raw ZIP, thÃƒÂ¬ sau nÃƒÂ y code sÃ¡ÂºÂ½ rÃ¡Â»â€˜i.