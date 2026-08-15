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

@app.command("train")
def train_model(
    config: Path = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to the model YAML config file (e.g., configs/quant_15m_1h.yaml).",
    )
) -> None:
    """Huấn luyện mô hình Quant AI bằng Walk-Forward CV và Optuna."""
    from finsight.experts.quant.training.pipeline import TrainingPipeline
    from finsight.config.settings import get_settings
    
    if not config.exists():
        typer.secho(f"Config file not found: {config}", fg=typer.colors.RED)
        raise typer.Exit(1)
        
    with config.open("r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)
        
    typer.secho(f"Training model: {config_dict.get('model_name')}", fg=typer.colors.CYAN)
    
    settings = get_settings()
    
    # Ưu tiên tìm dataset_name (dùng chung), nếu không có thì lấy model_name
    ds_name = config_dict.get('dataset_name', config_dict.get('model_name'))
    data_path = Path("data/gold") / f"{ds_name}.parquet"
    
    if not data_path.exists():
        typer.secho(f"Gold dataset not found at {data_path}. Please run build-dataset first.", fg=typer.colors.RED)
        raise typer.Exit(1)
        
    pipeline = TrainingPipeline(config=config_dict, data_path=data_path)
    model_dir = pipeline.run()
    
    typer.secho(f"✅ Training completed! Model and reports saved at: {model_dir}", fg=typer.colors.GREEN)


@app.command("train-all")
def train_all_models(config_dir: Path = typer.Option(Path("configs"), "--dir", "-d"), pattern: str = typer.Option("quant_1d_5d_*.yaml", "--pattern", "-p")) -> None:
    """Huấn luyện hàng loạt mô hình từ các file config."""
    from finsight.experts.quant.training.pipeline import TrainingPipeline
    if not config_dir.exists():
        typer.secho(f"Directory not found: {config_dir}", fg=typer.colors.RED)
        raise typer.Exit(1)
    config_files = list(config_dir.glob(pattern))
    if not config_files:
        typer.secho(f"No config files found matching {pattern}", fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    typer.secho(f"Found {len(config_files)} config files to run.", fg=typer.colors.CYAN)
    for cfg_file in config_files:
        typer.secho(f"\nStarting pipeline for: {cfg_file.name}", fg=typer.colors.MAGENTA)
        with cfg_file.open("r", encoding="utf-8") as f_cfg:
            config_dict = yaml.safe_load(f_cfg)
        ds_name = config_dict.get("dataset_name", config_dict.get("model_name"))
        data_path = Path("data/gold") / f"{ds_name}.parquet"
        if not data_path.exists():
            typer.secho(f"Gold dataset not found. Skipping.", fg=typer.colors.RED)
            continue
        try:
            pipeline = TrainingPipeline(config=config_dict, data_path=data_path)
            model_dir = pipeline.run()
            typer.secho(f"Training success! Saved at: {model_dir}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"Training failed: {e}", fg=typer.colors.RED)
    typer.secho(f"\nAll Batch Training completed!", fg=typer.colors.GREEN)
