import sys
from loguru import logger
from app.config import settings

def setup_logging():
    # Remove default handler
    logger.remove()

    # Add stdout handler with colors for Railway/Docker
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=True, # Thread-safe
        backtrace=True,
        diagnose=True,
    )

    # Keep file logging for persistence if needed (optional, but good for debug)
    logger.add(
        "bot.log",
        rotation="10 MB",
        retention="10 days",
        level="DEBUG",
        compression="zip",
        enqueue=True,
    )

setup_logging()
