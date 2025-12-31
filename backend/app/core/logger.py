"""
日志配置
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

from app.core.config import get_settings

settings = get_settings()


def setup_logger():
    """配置日志系统"""

    # 创建logs目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 配置formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 配置root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # 清除现有handlers
    logger.handlers.clear()

    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件handler - 所有日志
    today = datetime.now().strftime("%Y-%m-%d")
    all_log_file = log_dir / f"app_{today}.log"
    file_handler = logging.FileHandler(all_log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 文件handler - 错误日志
    error_log_file = log_dir / f"error_{today}.log"
    error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # 第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)

    logger.info("日志系统初始化完成")

    return logger


# 初始化日志
logger = setup_logger()
