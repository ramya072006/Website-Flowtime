"""Centralised logging configuration for the automation framework."""

import os
import logging
import logging.handlers
from datetime import datetime

try:
    import colorlog
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

from automation.config import path_config, test_config


def get_logger(name: str) -> logging.Logger:
    """Get a named logger with file + console handlers."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_level = getattr(logging, test_config.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Ensure log directory exists
    path_config.ensure_all()
    log_file = os.path.join(
        path_config.logs,
        f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    # File handler — detailed
    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))

    # Console handler
    if HAS_COLOR:
        ch = colorlog.StreamHandler()
        ch.setFormatter(colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s | %(levelname)-8s%(reset)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan', 'INFO': 'green',
                'WARNING': 'yellow', 'ERROR': 'red', 'CRITICAL': 'bold_red',
            }
        ))
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        ))
    ch.setLevel(log_level)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
