from datetime import datetime
from typing import Annotated, Optional

from beanie import Document, Indexed  # type: ignore
from pydantic import Field


class UserModel(Document):
    auth_id: Annotated[str, Indexed(unique=True)]
    first_name: str
    last_name: str
    email: Annotated[str, Indexed(unique=True)]
    phone_number: str
    role: Optional[str] = None
    hire_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"
