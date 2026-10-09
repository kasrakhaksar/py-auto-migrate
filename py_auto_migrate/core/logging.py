"""Central logging configuration.

Libraries only obtain loggers from this module; configuration is performed by
the application entry point so importing the package never changes the host
application's logging setup.
"""

import logging
from pathlib import Path


LOGGER_NAME = "py_auto_migrate"
DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger below the application's logger namespace."""
    if not name:
        return logging.getLogger(LOGGER_NAME)
    if name.startswith(LOGGER_NAME):
        return logging.getLogger(name)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")


def configure_logging(
    level: int = logging.INFO,
    log_file: str | Path | None = None,
) -> None:
    """Configure console logging once for CLI/dashboard entry points."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(DEFAULT_FORMAT))
        logger.addHandler(console)

    if log_file and not any(
        isinstance(handler, logging.FileHandler)
        and Path(handler.baseFilename) == Path(log_file).resolve()
        for handler in logger.handlers
    ):
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
        logger.addHandler(file_handler)
