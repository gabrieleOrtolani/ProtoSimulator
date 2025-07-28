import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(
    name="protosimulator",
    log_file="protosimulator.log",
    level=None
):
    level = level or os.environ.get("LOGLEVEL", "INFO")
    level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] %(message)s')

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Rotating file handler
    fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logger.propagate = False
    return logger

logger = setup_logger()