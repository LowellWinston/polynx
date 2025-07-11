import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(
    name: str = "polynx",
    level: int = logging.INFO,
    to_console: bool = True,
    to_file: str | None = None,
    rotate: bool = False,
    max_bytes: int = 1_000_000,
    backup_count: int = 3
):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s [%(name)s][%(levelname)s] %(message)s")

    if to_console:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    if to_file:
        os.makedirs(os.path.dirname(to_file), exist_ok=True)
        if rotate:
            fh = RotatingFileHandler(to_file, maxBytes=max_bytes, backupCount=backup_count)
        else:
            fh = logging.FileHandler(to_file, mode="w")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
