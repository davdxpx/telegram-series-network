from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application Configuration loaded from .env file
    """
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    BOT_TOKEN: str
    OWNER_TELEGRAM_ID: int
    TMDB_API_KEY: str
    MONGO_URI: str
    REDIS_URL: str
    BASE_URL: str
    SECRET_KEY: str
    LOG_LEVEL: str = "INFO"

settings = Settings()
