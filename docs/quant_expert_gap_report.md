# Crypto Quant Expert Gap Report

## Repository State

The workspace initially contained only the source PDF prompt:

- `Prompt_Codex_Crypto_Quant_Expert_Day_Du.pdf`

There was no existing Python package, API service, database layer, ingestion code, model training
code, Docker setup, or tests to reuse.

## Existing Components

None.

## Reusable Components

None from source code. The PDF specification is the authoritative product and engineering brief.

## Architecture Gaps

- No modular source tree under `src/`.
- No Binance market-data provider.
- No universe builder.
- No database schema or migrations.
- No ingestion pipeline for Binance Public Data ZIP or REST incremental backfill.
- No feature engineering, labeling, model training, backtest, model registry, realtime streaming,
  API, risk engine, monitoring, Docker, or CI.

## Phase Plan

### Phase 0 - Foundation

- Create Python project metadata.
- Create package structure.
- Add docs and progress tracking.
- Add test and lint configuration.

### Phase 1 - Binance Provider And Universe

- Implement Binance public REST client for ping, time, exchangeInfo, and 24hr ticker.
- Implement symbol validation rules for Binance Spot USDT.
- Implement universe builder with required symbols, candidate symbols, volume ranking, and
  rejection reasons.
- Add CLI command to build a universe report.
- Add unit tests with mocked provider data.

### Later Phases

- Phase 2: historical ingestion.
- Phase 3: features and dataset.
- Phase 4: training and backtest.
- Phase 5: realtime stream and reconciliation.
- Phase 6: FastAPI and risk engine.
- Phase 7: hardening, Docker, documentation, and CI.

## Files Created In Phase 0 And 1

- `pyproject.toml`
- `.env.example`
- `README.md`
- `PROGRESS.md`
- `docs/quant_expert_gap_report.md`
- `docs/universe_report.example.json`
- `src/finsight/...`
- `tests/...`

## Assumptions

- Python 3.12 is the target runtime.
- Binance public market data endpoints require no API key.
- Phase 1 does not require a database connection; database persistence starts in Phase 2 unless
  the user approves adding migrations earlier.
- Universe reports are written as JSON artifacts under `data/gold/universe/`.

