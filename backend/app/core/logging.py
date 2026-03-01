import sys
from loguru import logger
from app.core.config import get_settings


settings = get_settings()

logger.remove()
logger.add(
    sys.stdout,
    level="DEBUG" if settings.debug else "INFO",
    serialize=True,
    backtrace=settings.debug,
    diagnose=settings.debug,
)
