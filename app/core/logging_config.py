"""Logging configuration for the application."""
import logging
from app.core.config_loader import settings

logger = logging.getLogger("planorama")
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.WARNING)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if settings.DEBUG else logging.WARNING)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

