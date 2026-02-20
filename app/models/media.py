from typing import List, Optional, Dict
from datetime import datetime
from beanie import Document, Link, PydanticObjectId
from pydantic import Field

# We need forward references or careful ordering.
# Series -> Season -> Episode.

class Episode(Document):
    season_id: PydanticObjectId = Field(index=True)
    series_id: PydanticObjectId = Field(index=True) # Denormalized for easier queries
    network_id: PydanticObjectId = Field(index=True) # Denormalized for access control

    episode_number: int
    name: Optional[str] = None
    overview: Optional[str] = None
    still_path: Optional[str] = None # TMDB image

    file_id: str = Field(description="Telegram File ID (permanent from storage channel)")
    file_unique_id: str = Field(index=True, description="Telegram Unique File ID")
    file_size: Optional[int] = None
    duration: Optional[int] = None # Seconds

    tmdb_id: Optional[int] = Field(index=True, default=None)
    air_date: Optional[str] = None

    # Watch progress: {str(user_id): seconds_watched}
    # Using dict with string keys because MongoDB keys must be strings
    watch_progress: Dict[str, int] = Field(default_factory=dict)

    added_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "episodes"
        indexes = [
            ("series_id", "season_id", "episode_number"), # Compound index
        ]

class Season(Document):
    series_id: PydanticObjectId = Field(index=True)
    network_id: PydanticObjectId = Field(index=True)

    season_number: int
    name: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    air_date: Optional[str] = None

    episode_count: int = 0

    # We could embed episodes, but Documents are better for scaling (watching progress updates on episode shouldn't lock season)
    # So we reference them or just query by season_id. The requirement says: "episodes list of embedded or referenced"
    # Let's use referencing by ID (implicitly via Episode.season_id) to avoid massive documents.
    # However, to strictly follow "list of referenced" in schema description:
    # "Season (series_id, season_number, episodes list)"
    # We can store a list of IDs if requested, but query-based is more robust.
    # Let's stick to query-based 1-to-many for Episodes->Season for performance,
    # but we can add a helper or ignore the strict list field if "referenced" implies strict schema.
    # Actually, keeping a list of IDs in Season is fine if we maintain it.
    # Let's trust the "Virtual Library Structure" -> "Series -> Seasons -> Episodes" visualization
    # relies on queries.

    class Settings:
        name = "seasons"
        indexes = [
            ("series_id", "season_number"),
        ]

class Series(Document):
    network_id: PydanticObjectId = Field(index=True)

    tmdb_id: int = Field(index=True)
    title: str
    original_title: Optional[str] = None

    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    overview: Optional[str] = None

    genres: List[str] = []
    rating: Optional[float] = None # Vote average
    first_air_date: Optional[str] = None

    # "seasons list of embedded or referenced"
    # We will query seasons by series_id

    added_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "series"
