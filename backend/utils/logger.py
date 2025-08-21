import sys
import logging
from datetime import datetime


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """Setup logger with console and file handlers"""

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # avoid adding handlers multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(f'app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger