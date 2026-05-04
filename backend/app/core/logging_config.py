# sonic_library/logging_config.py
import logging
from logging.config import dictConfig
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def setup_logging():
    log_dir = "logs"
    file_logging_available = False
    try:
        os.makedirs(log_dir, exist_ok=True)
        file_logging_available = True
    except OSError:
        pass

    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    }
    sonic_handlers = ["console"]

    if file_logging_available:
        handlers["file"] = {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "logs/sonic.log",
            "mode": "a",
        }
        sonic_handlers.append("file")

    dictConfig({
      "version": 1,
      "disable_existing_loggers": False,
      "formatters": {
          "default": {
              "format": "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
          },
      },
      "handlers": handlers,
      "root": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
    },
      "loggers": {
          "sonic": {
              "handlers": sonic_handlers,
              "level": LOG_LEVEL,
              "propagate": False,
          },
          "uvicorn": {
              "handlers": ["console"],
              "level": "INFO",
              "propagate": False,
          },
      }
  })