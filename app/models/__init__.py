import os
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import Field
from beanie import Document, Indexed, Link

class AdminSettings(Document):
    """
    Singleton document storing global settings for the Single Network.
    Since this is a single-network bot, we only need one of these.
    """
    owner_telegram_id: int = Indexed(unique=True)
    tmdb_api_key: Optional[str] = None
    bot_name: str = "Telegram Series Network"
    maintenance_mode: bool = False

    class Settings:
        name = "admin_settings"

class StorageChannel(Document):
    """
    Represents a Telegram Channel where media files are stored.
    The bot must be an Admin in these channels.
    """
    channel_id: int = Indexed(unique=True)
    invite_link: Optional[str] = None
    name: str
    total_files: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "storage_channels"

class Bundle(Document):
    """
    A curated collection of Series (e.g., 'Marvel Universe', 'Best of 2024').
    Episodes belong to a Series, but the Series belongs to a Bundle for organization.
    """
    name: str = Indexed(unique=True)
    description: Optional[str] = None
    cover_image: Optional[str] = None  # URL or File ID
    slug: str = Indexed(unique=True)   # For URL friendly links
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    series_count: int = 0

    class Settings:
        name = "bundles"

class Series(Document):
    """
    Represents a TV Show.
    Metadata fetched from TMDB.
    """
    tmdb_id: int = Indexed(unique=True)
    name: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    first_air_date: Optional[str] = None
    rating: float = 0.0

    # Relationship to Bundle
    bundle_id: Link[Bundle]

    class Settings:
        name = "series"

class Season(Document):
    """
    Represents a Season of a Series.
    """
    series_id: Link[Series]
    season_number: int
    name: str
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    air_date: Optional[str] = None
    episode_count: int = 0

    class Settings:
        name = "seasons"
        # Compound index for fast lookup of a specific season in a series
        indexes = [
            [("series_id", 1), ("season_number", 1)]
        ]

class Episode(Document):
    """
    Represents a single video file (Episode).
    Stores the link to the actual file in the Storage Channel.
    """
    series_id: Link[Series]
    season_id: Link[Season]

    episode_number: int
    name: str
    overview: Optional[str] = None
    still_path: Optional[str] = None
    air_date: Optional[str] = None
    runtime: Optional[int] = None

    # File Storage Info
    storage_channel_id: int
    message_id: int        # The message ID in the channel
    file_id: str           # The Telegram File ID (for sending via bot)
    file_unique_id: str    # Unique ID for duplicate detection
    file_size: int
    mime_type: Optional[str] = None

    # Import Metadata
    original_filename: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "episodes"
        indexes = [
            [("series_id", 1), ("season_id", 1), ("episode_number", 1)],
            "file_unique_id"
        ]

class User(Document):
    """
    Represents a Bot User.
    Since this is a private network, roles are important.
    """
    telegram_id: int = Indexed(unique=True)
    username: Optional[str] = None
    full_name: str
    role: str = "viewer"  # viewer, uploader, moderator, admin

    is_banned: bool = False
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    # Watch History & Progress
    # stored as {episode_id_str: timestamp_seconds}
    watch_progress: Dict[str, float] = {}

    # Stats
    total_watch_time: int = 0 # in seconds

    class Settings:
        name = "users"
