.PHONY: test compile universe-plan history-plan

test:
	pytest -p no:cacheprovider

compile:
	python -m compileall -q src tests apps scripts

universe-plan:
	python -m finsight.cli universe build --quote-asset USDT --limit 10 --dry-run

history-plan:
	python -m finsight.cli market backfill --symbols BTCUSDT,ETHUSDT --intervals 15m --start 2026-01-01 --end 2026-03-31 --mode monthly-zip --dry-run