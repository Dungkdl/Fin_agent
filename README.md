# FinSight Agent - Crypto Quant Expert

FinSight Agent is a research-first market analysis project. This repository currently contains
the Phase 0 and Phase 1 foundation for Crypto Quant Expert v1.

## Scope

- Asset type: crypto
- Exchange: Binance
- Trading mode: Spot only
- Quote asset: USDT
- Required symbols: BTCUSDT, ETHUSDT
- Candidate symbols: SOLUSDT, BNBUSDT, XRPUSDT, ADAUSDT, DOGEUSDT, LINKUSDT

This project does not call trading endpoints, request trading permissions, or provide financial
advice.

## Phase 1 Commands

Build a universe from Binance public market data:

```bash
python -m finsight.cli universe build --quote-asset USDT --limit 10
```

Use dry-run to inspect the request without writing reports:

```bash
python -m finsight.cli universe build --quote-asset USDT --limit 10 --dry-run
```

## Tests

```bash
pytest
```


## Code Structure

See docs/code_structure.md for the repository layout aligned with the PDF specification.

For a detailed file-by-file explanation and dependency flow, read docs/quant_expert_file_map.md.

Reading guide: docs/how_to_read_quant_expert_code.md.

Multi-expert architecture: docs/multi_expert_architecture.md.
