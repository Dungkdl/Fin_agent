from datetime import date

import pytest

from finsight.crawl.backfill_plan import BackfillRequest, HistoricalBackfillPlanner
from finsight.config.crawl_constants import BackfillMode


def test_backfill_request_from_cli_normalizes_values() -> None:
    request = BackfillRequest.from_cli(
        symbols="btcusdt, ethusdt",
        intervals="15m,1h",
        start="2026-01-01",
        end="2026-03-31",
        mode="monthly-zip",
    )

    assert request.symbols == ("BTCUSDT", "ETHUSDT")
    assert request.intervals == ("15m", "1h")
    assert request.start == date(2026, 1, 1)
    assert request.end == date(2026, 3, 31)
    assert request.mode == BackfillMode.MONTHLY_ZIP


def test_backfill_request_rejects_bad_mode() -> None:
    with pytest.raises(ValueError):
        BackfillRequest.from_cli(
            symbols="BTCUSDT",
            intervals="15m",
            start="2026-01-01",
            end="2026-01-31",
            mode="bad",
        )


def test_historical_backfill_planner_builds_monthly_zip_plan() -> None:
    request = BackfillRequest.from_cli(
        symbols="BTCUSDT,ETHUSDT",
        intervals="15m",
        start="2026-01-01",
        end="2026-03-31",
        mode="monthly-zip",
    )

    plan = HistoricalBackfillPlanner().plan(request)

    assert len(plan.monthly_files) == 6
    assert plan.urls[0].endswith("BTCUSDT/15m/BTCUSDT-15m-2026-01.zip")
    assert plan.urls[-1].endswith("ETHUSDT/15m/ETHUSDT-15m-2026-03.zip")