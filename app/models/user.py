from typing import List, Optional
from datetime import datetime
from beanie import Document, Link
from pydantic import Field
from enum import Enum

class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    UPLOADER = "uploader"
    VIEWER = "viewer"

class User(Document):
    telegram_id: int = Field(index=True, unique=True)
    username: Optional[str] = None
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Store network IDs the user is part of.
    # We reference Network by ID string to avoid circular imports if possible,
    # but Beanie handles Link well. using simple list of IDs is often safer for simple many-to-many.
    # However, for now let's store references if we need to access network details often.
    # Given the requirements: "networks list of references"
    # We will use Link later if needed, but Pydantic v2 often prefers simple ID lists for clean serialization
    # unless using Beanie's fetch features. Let's use list of Pydantic ObjectIds for now which Beanie uses.

    # Actually, let's keep it simple: A user can belong to multiple networks.
    # We'll store a list of Network IDs. Beanie uses PydanticObjectId.
    # But wait, to avoid circular imports with Network model, we might define this update later
    # or just use PydanticObjectId.

    class Settings:
        name = "users"
