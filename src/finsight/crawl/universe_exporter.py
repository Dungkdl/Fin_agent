"""Ghi kết quả build universe ra file JSON trong data/gold/universe."""

import json
from pathlib import Path

from finsight.crawl.coin_selector import UniverseBuildResult


class UniverseReportWriter:
    def __init__(self, output_dir: Path = Path("data/gold/universe")) -> None:
        self.output_dir = output_dir

    def write(self, result: UniverseBuildResult) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{result.universe_name}.json"
        path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path

