from typing import List, Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    BOT_TOKEN: str
    TMDB_API_KEY: str
    MONGO_URI: str
    # Make REDIS_URL optional with a default or None if not strictly required for startup checks
    # However, app logic might depend on it. Let's provide a default or make it Optional.
    REDIS_URL: Optional[str] = None

    SECRET_KEY: str = "unsafe_secret_key_change_me"
    BASE_URL: Optional[str] = None # For WebApp absolute URLs

    # Allow ADMIN_IDS to be parsed from a comma-separated string
    ADMIN_IDS: List[int] = Field(default_factory=list)
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: Union[str, int, List[Any]]) -> List[int]:
        if isinstance(v, str):
            # Handle comma-separated string "123,456"
            if not v.strip():
                return []
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        if isinstance(v, int):
            # Handle single integer case
            return [v]
        return v

settings = Settings()
