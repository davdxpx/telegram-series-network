from typing import List, Optional
from datetime import datetime
from beanie import Document, Link, PydanticObjectId
from pydantic import Field
from app.models.user import User

class Network(Document):
    name: str
    owner_id: int = Field(description="Telegram ID of the owner")
    invite_code: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Members: List of User references or just their IDs?
    # Requirement: "members list of references"
    # We will use Link[User] to use Beanie's fetch capabilities
    members: List[Link[User]] = []

    # Private storage channels for this network
    storage_channel_ids: List[int] = Field(default_factory=list, description="List of Telegram Channel IDs used for storage")

    class Settings:
        name = "networks"
