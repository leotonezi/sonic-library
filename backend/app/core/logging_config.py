# sonic_library/logging_config.py
import logging
from logging.config import dictConfig
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    dictConfig({
      "version": 1,
      "disable_existing_loggers": False,
      "formatters": {
          "default": {
              "format": "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
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
      }
  })