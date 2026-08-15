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
    import logging
    logger = logging.getLogger(__name__)

    if not config.exists():
        msg = f"Config file not found: {config}"
        typer.secho(msg, fg=typer.colors.RED)
        logger.error(msg)
        raise typer.Exit(1)
        
    with config.open("r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)
        
    msg = f"Building dataset for model: {config_dict.get('model_name')}"
    typer.secho(msg, fg=typer.colors.CYAN)
    logger.info(msg)
    
    settings = get_settings()
    silver_storage = SilverCandleStorage(settings.ingestion.storage)
    
    builder = DatasetBuilder(config=config_dict, silver_storage=silver_storage)
    
    out_file = builder.build_dataset()
    
    if out_file and out_file.exists():
        msg = f"Dataset successfully built at: {out_file}"
        typer.secho(msg, fg=typer.colors.GREEN)
        logger.info(msg)
    else:
        msg = "Failed to build dataset (maybe missing data)."
        typer.secho(msg, fg=typer.colors.RED)
        logger.error(msg)
        raise typer.Exit(1)

@app.command("train")
def train_model(
    config: Path = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to the model YAML config file (e.g., configs/quant_1d_5d.yaml).",
    ),
    engine: str = typer.Option(
        None,
        "--engine",
        "-e",
        help="Override model engine (lightgbm, xgboost, catboost, logistic_regression).",
    )
) -> None:
    """Huấn luyện mô hình Quant AI bằng Walk-Forward CV và Optuna."""
    from finsight.experts.quant.training.pipeline import TrainingPipeline
    
    import logging
    logger = logging.getLogger(__name__)

    if not config.exists():
        msg = f"Config file not found: {config}"
        typer.secho(msg, fg=typer.colors.RED)
        logger.error(msg)
        raise typer.Exit(1)
        
    with config.open("r", encoding="utf-8") as f:
        config_dict = yaml.safe_load(f)
        
    ds_name = config_dict.get('dataset_name', config_dict.get('model_name'))
    
    if engine:
        config_dict['model']['type'] = engine
        config_dict['model_name'] = f"{ds_name}_{engine}"
        
    msg = f"Training model: {config_dict.get('model_name')} (Engine: {config_dict['model']['type']})"
    typer.secho(msg, fg=typer.colors.CYAN)
    logger.info(msg)
    
    data_path = Path("data/gold/training_samples") / f"{ds_name}.parquet"
    
    if not data_path.exists():
        msg = f"Gold dataset not found at {data_path}. Please run build-dataset first."
        typer.secho(msg, fg=typer.colors.RED)
        logger.error(msg)
        raise typer.Exit(1)
        
    pipeline = TrainingPipeline(config=config_dict, data_path=data_path)
    model_dir = pipeline.run()
    
    msg = f"[OK] Training completed! Model and reports saved at: {model_dir}"
    typer.secho(msg, fg=typer.colors.GREEN)
    logger.info(msg)


@app.command("train-all")
def train_all_models(
    config: Path = typer.Option(
        Path("configs/quant_1d_5d.yaml"),
        "--config",
        "-c",
        help="Path to the base YAML config file."
    )
) -> None:
    """Huấn luyện hàng loạt tất cả mô hình (LGB, XGB, CAT, LogReg) từ 1 file config gốc."""
    from finsight.experts.quant.training.pipeline import TrainingPipeline
    import logging
    logger = logging.getLogger(__name__)
    
    if not config.exists():
        msg = f"Config file not found: {config}"
        typer.secho(msg, fg=typer.colors.RED)
        logger.error(msg)
        raise typer.Exit(1)
        
    with config.open("r", encoding="utf-8") as f:
        base_config = yaml.safe_load(f)
        
    ds_name = base_config.get("dataset_name", base_config.get("model_name"))
    data_path = Path("data/gold/training_samples") / f"{ds_name}.parquet"
    
    if not data_path.exists():
        msg = f"Gold dataset not found at {data_path}. Please run build-dataset first."
        typer.secho(msg, fg=typer.colors.RED)
        logger.error(msg)
        raise typer.Exit(1)

    engines = ['lightgbm', 'xgboost', 'catboost', 'logistic_regression']
    
    for engine in engines:
        typer.secho(f"\n{'='*50}", fg=typer.colors.MAGENTA)
        msg = f"Starting pipeline for Engine: {engine.upper()}"
        typer.secho(msg, fg=typer.colors.MAGENTA)
        logger.info(msg)
        typer.secho(f"{'='*50}\n", fg=typer.colors.MAGENTA)
        
        cfg = base_config.copy()
        # Ensure deep copy of model dict to avoid overwriting base
        cfg['model'] = base_config['model'].copy()
        
        cfg['model']['type'] = engine
        cfg['model_name'] = f"{ds_name}_{engine}"
        
        try:
            pipeline = TrainingPipeline(config=cfg, data_path=data_path)
            model_dir = pipeline.run()
            msg = f"✅ Training success! Saved at: {model_dir}"
            typer.secho(msg, fg=typer.colors.GREEN)
            logger.info(msg)
        except Exception as e:
            msg = f"❌ Training failed for {engine}: {e}"
            typer.secho(msg, fg=typer.colors.RED)
            logger.error(msg)
            
    msg = f"\n🎉 All Batch Training completed!"
    typer.secho(msg, fg=typer.colors.GREEN)
    logger.info(msg.strip())
