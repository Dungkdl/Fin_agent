"""CLI command cho việc chạy pipeline Quant (Feature & Dataset)."""

import typer
import yaml
from pathlib import Path

from finsight.config.settings import get_settings
from finsight.database.parquet_storage import SilverCandleStorage
from finsight.experts.quant.datasets.builder import DatasetBuilder

app = typer.Typer(help="Quant ML dataset and training commands.")


@app.command("build-dataset")
def build_dataset(
    config: Path = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to the model YAML config file (e.g., configs/quant_15m_1h.yaml).",
    )
) -> None:
    """Xây dựng dataset tổng hợp (Features, Labels, Weights) từ Silver layer."""
    if not config.exists():
        typer.secho(f"Config file not found: {config}", fg=typer.colors.RED)
        raise typer.Exit(1)
        
    with config.open("r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)
        
    typer.secho(f"Building dataset for model: {config_dict.get('model_name')}", fg=typer.colors.CYAN)
    
    settings = get_settings()
    silver_storage = SilverCandleStorage(settings.ingestion.storage)
    
    builder = DatasetBuilder(config=config_dict, silver_storage=silver_storage)
    
    out_file = builder.build_dataset()
    
    if out_file and out_file.exists():
        typer.secho(f"Dataset successfully built at: {out_file}", fg=typer.colors.GREEN)
    else:
        typer.secho("Failed to build dataset (maybe missing data).", fg=typer.colors.RED)
        raise typer.Exit(1)
