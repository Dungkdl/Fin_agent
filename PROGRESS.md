# PROGRESS

## Phase 0 - Foundation

Status: complete

Deliverables:

- Created Python project metadata in `pyproject.toml`.
- Created package structure under `src/finsight`.
- Created `README.md`, `.env.example`, `.gitignore`.
- Created `docs/quant_expert_gap_report.md`.

## Phase 1 - Binance Provider And Universe

Status: complete

Deliverables:

- Implemented Binance public REST client for `/api/v3/ping`, `/api/v3/time`, `/api/v3/exchangeInfo`, and `/api/v3/ticker/24hr`.
- Implemented Binance ticker and symbol schemas.
- Implemented millisecond/microsecond timestamp parser.
- Implemented runtime universe builder with required symbols, candidate symbols, quote asset checks, Spot checks, stablecoin-pair rejection, leveraged-token rejection, and quote-volume filtering.
- Implemented CLI command: `python -m finsight.cli universe build`.
- Created universe report artifact: `data/gold/universe/crypto_spot_usdt_v1_20260725T080739Z.json`.
- Added unit tests for REST client behavior, timestamp parsing, and universe selection/rejection rules.

## Phase 2 - Historical Ingestion

Status: written and verified without downloading market data

Deliverables:

- Refactored Phase 2 toward OOP/config constants for maintainability.
- Added ingestion constants for backfill modes, source types, default roots, limits, timeout, and filenames.
- Added ingestion config dataclasses for bulk download, REST backfill, and storage.
- Added `BackfillRequest`, `BackfillPlan`, and `HistoricalBackfillPlanner` so CLI no longer owns planning logic.
- Implemented Binance Public Data monthly/daily kline URL builder.
- Implemented checksum parser and SHA-256 verification.
- Implemented safe ZIP extraction with zip-slip protection.
- Implemented bronze local path planner for ZIP and CHECKSUM files.
- Implemented bronze download metadata writer.
- Implemented REST kline endpoint support in Binance REST client.
- Implemented REST kline normalizer preserving the 11 required stored fields and dropping Binance `ignore`.
- Implemented REST backfill pagination by `startTime`.
- Implemented candle validation for duplicate rows, missing candles, invalid OHLC, negative volume, and timestamp errors.
- Implemented Silver Parquet writer with partitioning and batch deduplication.
- Implemented dry-run CLI planner: `python -m finsight.cli market backfill`.
- Added unit tests for URL builder, checksum, safe ZIP extraction, kline parser, validator, and REST backfill pagination.

## Commands Run

- `pytest`
  - Initial Phase 1 result: failed because async tests depended on missing `pytest-asyncio`.
- `pytest -p no:cacheprovider`
  - Phase 1 final result: 6 passed.
  - Phase 2 final result after OOP/config refactor: 20 passed.
- `python -m compileall -q src tests`
  - Result: passed.
- `ruff check src tests`
  - Result: not run because `ruff` is not installed in the current Python environment.
- `$env:PYTHONPATH='src'; python -m finsight.cli universe build --quote-asset USDT --limit 10 --dry-run`
  - Initial result: sandbox network connection failed.
- `$env:PYTHONPATH='src'; python -m finsight.cli universe build --quote-asset USDT --limit 10 --dry-run`
  - Rerun with approved network access: success.
  - Selected: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT, DOGEUSDT, DEXEUSDT, AEROUSDT, VANAUSDT, ZECUSDT.
- `$env:PYTHONPATH='src'; python -m finsight.cli universe build --quote-asset USDT --limit 10`
  - Rerun with approved network access: success.
  - Report written: `data/gold/universe/crypto_spot_usdt_v1_20260725T080739Z.json`.
- `$env:PYTHONPATH='src'; python -m finsight.cli market backfill --symbols BTCUSDT,ETHUSDT --intervals 15m --start 2026-01-01 --end 2026-03-31 --mode monthly-zip --dry-run`
  - Result: success.
  - Only printed planned Binance Public Data URLs; no files were downloaded.

## Notes

- Full historical backfill has not been run.
- No Binance ZIP/CSV candle data has been downloaded.
- No trading endpoints are implemented.
- During runtime validation, `RLUSDUSDT` appeared as a high-volume stablecoin pair and was rejected after adding `RLUSD` to the stablecoin exclusion list.
- Phase 2 currently provides filesystem ingestion primitives, Bronze metadata writing, Silver Parquet writing, REST pagination, and validation logic. Database persistence, ingestion run rows, and candle upsert repositories should be completed before running real backfills at scale.
- Phase 3 should start with shared FeatureBuilder, label builder, sample weights, and gold dataset generation.
## Structure Alignment

Status: complete

- Re-read the PDF code structure section and aligned the repository layout with it.
- Added `apps/api/main.py` and `apps/worker/main.py` entrypoints.
- Added `configs/` files for development, ingestion, and the three quant model tasks.
- Added `scripts/` wrappers only for implemented Phase 1/2 commands, with planned later scripts documented instead of fake Python modules.
- Moved tests into `tests/unit/` and reserved `tests/integration/` plus `tests/end_to_end/`.
- Added namespace directories for future `database`, `quant`, `risk`, `services`, `api`, and `monitoring` modules.
- Added `docs/code_structure.md` as the readable map of the repo.
- Verification after restructuring: `pytest -p no:cacheprovider` passed with 21 tests.
## Download Command Readiness

Status: complete

- Wired `market backfill --no-dry-run` to execute monthly ZIP downloads through `HistoricalIngestionService`.
- The execution path downloads ZIP and CHECKSUM files, verifies SHA-256, safely extracts CSV files, and writes bronze metadata.
- Verification after wiring execution: `pytest -p no:cacheprovider` passed with 22 tests.
- Real market-data download has still not been run by Codex in this step.
## Simplified Structure

Status: complete

- Simplified source layout per user request without changing existing logic.
- Moved configuration files into `src/finsight/config`.
- Moved Binance crawling and ingestion files into `src/finsight/crawl`.
- Moved filesystem storage into `src/finsight/database/storage.py`.
- Removed old empty namespace folders that made the tree hard to read.
- Kept `src/finsight/experts/quant` as the simple Phase 3 home for Quant Expert code.
- Verification after move: `pytest -p no:cacheprovider` passed with 22 tests and compile passed.
## Multi Expert Layout

Status: complete

- Moved Quant placeholder from `src/finsight/quant` to `src/finsight/experts/quant`.
- Added placeholder expert folders for `news`, `fundamental`, and `fusion` with README guidance only.
- Added `src/finsight/domain/expert.py` with common expert output schemas.
- Added `docs/multi_expert_architecture.md`.
- Verification after move: `pytest -p no:cacheprovider` passed with 22 tests and compile passed.