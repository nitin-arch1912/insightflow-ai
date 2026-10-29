"""
Structured application logger.

We configure Python's standard logging library once here and expose a
factory function.  Every module gets its own named logger, which means
log output shows exactly which module produced each message.

Usage:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("Server starting", extra={"port": 8000})
"""

import logging
import sys

from app.core.config import settings

# Map string names to logging constants
_LOG_LEVELS: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _configure_root_logger() -> None:
    """Configure the root logger once when this module is first imported."""
    level = _LOG_LEVELS.get(settings.log_level.upper(), logging.INFO)

    # In production we would use a JSON formatter (e.g. python-json-logger).
    # For development, a readable format is more useful.
    if settings.app_env == "development":
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        datefmt = "%H:%M:%S"
    else:
        fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
        datefmt = "%Y-%m-%dT%H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


_configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for the given module."""
    return logging.getLogger(name)
