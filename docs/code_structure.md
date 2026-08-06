# Code Structure

Repo Ã„â€˜ÃƒÂ£ Ã„â€˜Ã†Â°Ã¡Â»Â£c sÃ¡ÂºÂ¯p xÃ¡ÂºÂ¿p lÃ¡ÂºÂ¡i theo hÃ†Â°Ã¡Â»â€ºng Ã„â€˜Ã†Â¡n giÃ¡ÂºÂ£n, dÃ¡Â»â€¦ Ã„â€˜Ã¡Â»Âc hÃ†Â¡n. MÃ¡Â»Â¥c tiÃƒÂªu lÃƒÂ  nhÃƒÂ¬n tÃƒÂªn folder lÃƒÂ  biÃ¡ÂºÂ¿t trÃƒÂ¡ch nhiÃ¡Â»â€¡m chÃƒÂ­nh.

```text
src/finsight/
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ cli/        # lÃ¡Â»â€¡nh terminal ngÃ†Â°Ã¡Â»Âi dÃƒÂ¹ng chÃ¡ÂºÂ¡y
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ config/     # settings, constants, config object
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ crawl/      # code lÃ¡ÂºÂ¥y dÃ¡Â»Â¯ liÃ¡Â»â€¡u tÃ¡Â»Â« Binance vÃƒÂ  xÃ¡Â»Â­ lÃƒÂ½ ingestion
Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ binance/ # code riÃƒÂªng cho Binance
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ database/   # code ghi/lÃ†Â°u dÃ¡Â»Â¯ liÃ¡Â»â€¡u
Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ domain/     # object/schema nghiÃ¡Â»â€¡p vÃ¡Â»Â¥ dÃƒÂ¹ng chung
Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ experts/quant/      # Phase 3: feature, label, dataset, model
```

## NhÃƒÂ³m ChÃƒÂ­nh

### cli

ChÃ¡Â»â€° nhÃ¡ÂºÂ­n input tÃ¡Â»Â« terminal rÃ¡Â»â€œi gÃ¡Â»Âi service. KhÃƒÂ´ng Ã„â€˜Ã¡Â»Æ’ business logic lÃ¡Â»â€ºn Ã¡Â»Å¸ Ã„â€˜ÃƒÂ¢y.

- `cli/main.py`: Ã„â€˜Ã„Æ’ng kÃƒÂ½ command group.
- `cli/universe.py`: command build universe.
- `cli/market.py`: command backfill dÃ¡Â»Â¯ liÃ¡Â»â€¡u market.

### config

ChÃ¡Â»Â©a cÃ¡ÂºÂ¥u hÃƒÂ¬nh vÃƒÂ  constant dÃƒÂ¹ng chung.

- `settings.py`: Ã„â€˜Ã¡Â»Âc env bÃ¡ÂºÂ±ng pydantic-settings.
- `constants.py`: symbol, interval, stablecoin, model task.
- `crawl_constants.py`: mode crawl, source type, default path, limit.
- `crawl_config.py`: config object cho downloader/backfill/storage.
- `time.py`: helper UTC.
- `logging.py`: logging setup.
- `exceptions.py`: exception chung.

### crawl

ChÃ¡Â»Â©a toÃƒÂ n bÃ¡Â»â„¢ code lÃ¡ÂºÂ¥y dÃ¡Â»Â¯ liÃ¡Â»â€¡u vÃƒÂ  xÃ¡Â»Â­ lÃƒÂ½ ingestion.

- `universe_builder.py`: chÃ¡Â»Ân danh sÃƒÂ¡ch coin hÃ¡Â»Â£p lÃ¡Â»â€¡.
- `universe_report.py`: ghi report universe.
- `backfill_plan.py`: lÃ¡ÂºÂ­p kÃ¡ÂºÂ¿ hoÃ¡ÂºÂ¡ch cÃ¡ÂºÂ§n tÃ¡ÂºÂ£i file nÃƒÂ o.
- `downloader.py`: tÃ¡ÂºÂ£i ZIP/CHECKSUM, verify SHA-256, giÃ¡ÂºÂ£i nÃƒÂ©n an toÃƒÂ n.
- `rest_backfill.py`: lÃ¡ÂºÂ¥y dÃ¡Â»Â¯ liÃ¡Â»â€¡u qua REST `/api/v3/klines`.
- `validator.py`: kiÃ¡Â»Æ’m tra chÃ¡ÂºÂ¥t lÃ†Â°Ã¡Â»Â£ng candle.
- `service.py`: nÃ¡Â»â€˜i planner, downloader, extractor, metadata writer.
- `binance/`: code cÃ¡Â»Â¥ thÃ¡Â»Æ’ cho Binance.

### database

ChÃ¡Â»Â©a code lÃ†Â°u dÃ¡Â»Â¯ liÃ¡Â»â€¡u.

- `storage.py`: ghi bronze metadata vÃƒÂ  silver parquet.

Sau nÃƒÂ y nÃ¡ÂºÂ¿u thÃƒÂªm PostgreSQL/Alembic thÃƒÂ¬ cÃ…Â©ng Ã„â€˜Ã¡Â»Æ’ trong `database/`.

### domain

ChÃ¡Â»Â©a object chung, khÃƒÂ´ng phÃ¡Â»Â¥ thuÃ¡Â»â„¢c Binance.

- `entities.py`: `Candle`.
- `enums.py`: enum asset/exchange/trading mode.
- `events.py`: event nghiÃ¡Â»â€¡p vÃ¡Â»Â¥.
- `schemas.py`: schema dÃƒÂ¹ng chung.

### quant

ChÃ†Â°a triÃ¡Â»Æ’n khai logic. Phase 3 sÃ¡ÂºÂ½ viÃ¡ÂºÂ¿t Ã¡Â»Å¸ Ã„â€˜ÃƒÂ¢y theo dÃ¡ÂºÂ¡ng Ã„â€˜Ã†Â¡n giÃ¡ÂºÂ£n:

- `features.py`
- `labels.py`
- `dataset.py`
- `models.py`
- `train.py`
- `predict.py`

## LuÃ¡Â»â€œng HiÃ¡Â»â€¡n TÃ¡ÂºÂ¡i

Build universe:

```text
cli/universe.py
  Ã¢â€ â€œ
crawl/binance/rest_client.py
  Ã¢â€ â€œ
crawl/universe_builder.py
  Ã¢â€ â€œ
crawl/universe_report.py
  Ã¢â€ â€œ
data/gold/universe/*.json
```

Download market ZIP:

```text
cli/market.py
  Ã¢â€ â€œ
crawl/service.py
  Ã¢â€ â€œ
crawl/backfill_plan.py
  Ã¢â€ â€œ
crawl/binance/public_data_client.py
  Ã¢â€ â€œ
crawl/downloader.py
  Ã¢â€ â€œ
database/storage.py
  Ã¢â€ â€œ
data/bronze/binance/spot/klines/...
```