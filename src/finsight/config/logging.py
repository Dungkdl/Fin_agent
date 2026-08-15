"""Cấu hình logging dùng chung cho app và worker."""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

def configure_logging(level: str = "INFO") -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "finsight.log"
    
    # Format chung
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    
    # 1. Stream handler (Console)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 2. File handler (xoay vòng file để không bị quá lớn)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    
    # Lấy root logger
    root_logger = logging.getLogger()
    
    # Xóa các handler cũ nếu có
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)