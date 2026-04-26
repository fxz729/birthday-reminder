"""集中日志配置"""
import logging
import sys
from pathlib import Path


def setup_logging(debug: bool = False) -> None:
    """配置日志格式，同时输出到控制台和文件"""
    level = logging.DEBUG if debug else logging.INFO
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
        ],
    )
