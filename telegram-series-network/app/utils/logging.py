import sys
from loguru import logger
from app.config import settings

def setup_logging():
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.add(
        "bot.log",
        rotation="10 MB",
        retention="10 days",
        level="DEBUG", # Always log debug to file
        compression="zip",
    )

setup_logging()
