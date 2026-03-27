import logging
from logging.config import dictConfig
import os

import structlog

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def _is_dev_environment() -> bool:
    """Detect if running in local/dev environment for human-readable logs."""
    env = os.getenv("ENV", "").lower()
    debug = os.getenv("DEBUG", "").lower()
    if debug in ("1", "true", "yes"):
        return True
    if env in ("development", "local", "dev"):
        return True
    return False


def setup_logging() -> None:
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Configure stdlib logging first (structlog wraps it)
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "filename": "logs/sonic.log",
                "mode": "a",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
        },
        "loggers": {
            "sonic": {
                "handlers": ["console", "file"],
                "level": LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    })

    # Shared processors for both structlog and stdlib integration
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if _is_dev_environment():
        # Human-readable colored output for local dev
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        # JSON output for production
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Update stdlib formatters to use structlog's ProcessorFormatter
    # so that existing logging.getLogger() calls also produce structured output
    structlog_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    # Apply structlog formatter to all existing handlers
    for handler in logging.root.handlers:
        handler.setFormatter(structlog_formatter)

    sonic_logger = logging.getLogger("sonic")
    for handler in sonic_logger.handlers:
        handler.setFormatter(structlog_formatter)
