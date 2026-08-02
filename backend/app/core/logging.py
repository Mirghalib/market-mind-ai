"""Logging configuration.

Call configure_logging() once at application startup. Keep the global
`logger` importable so modules can do:

    from app.core.logging import logger
"""
import logging
import sys

from app.core.config import settings

# Root logger for the app namespace; modules inherit handlers via propagation.
logger = logging.getLogger("market_mind_ai")

# Clean, structured access-log format used by request logging middleware.
ACCESS_LOG_FORMAT = (
    '%(asctime)s | %(levelname)-8s | request | '
    '%(message)s | %(duration_ms)s ms | request_id=%(request_id)s'
)


def configure_logging() -> None:
    """Idempotently configure the root logger."""
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root = logging.getLogger()
    if root.handlers:  # already configured (e.g. uvicorn did it)
        logger.setLevel(level)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.setLevel(level)
    logger.setLevel(level)
