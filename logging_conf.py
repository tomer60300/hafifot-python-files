import logging
from logging.config import dictConfig

def configure_logging(level: str = "INFO") -> None:
    dictConfig({
        "version": 1,
        "formatters": {
            "std": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "std",
                "level": level,
            }
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
        "disable_existing_loggers": False,
    })
