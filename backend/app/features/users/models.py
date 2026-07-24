from datetime import datetime
from typing import Annotated, Optional

import pymongo
from beanie import Document, Indexed  # type: ignore
from pydantic import Field


class UserModel(Document):
    auth_id: Annotated[str, Indexed(unique=True)]
    username: Annotated[str, Indexed(unique=True)]
    email: Annotated[str, Indexed(unique=True)]
    first_name: str
    last_name: str
    phone_number: str
    role: Optional[str] = None
    hire_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"
        indexes = [
            [("first_name", pymongo.ASCENDING), ("last_name", pymongo.ASCENDING)]
        ]
