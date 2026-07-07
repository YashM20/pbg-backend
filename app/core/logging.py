import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """Configure the global application logging format and level."""
    log_level = logging.INFO
    if settings.env == "dev":
        log_level = logging.DEBUG

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Configure root logger handlers
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        for h in root_logger.handlers:
            h.setFormatter(formatter)
            h.setLevel(log_level)

    # Adjust third-party library log levels to avoid noise
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("paddlex").setLevel(logging.INFO)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
