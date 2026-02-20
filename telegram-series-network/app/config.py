from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    BOT_TOKEN: str
    TMDB_API_KEY: str
    MONGO_URI: str
    REDIS_URL: str

    SECRET_KEY: str = "unsafe_secret_key_change_me"
    BASE_URL: Optional[str] = None # For WebApp absolute URLs

    ADMIN_IDS: List[int] = Field(default_factory=list)
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
