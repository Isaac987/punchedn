from datetime import datetime
from typing import Annotated, Optional

from beanie import Document, Indexed  # type: ignore


class User(Document):
    auth_id: Annotated[str, Indexed(unique=True)]
    first_name: str
    last_name: str
    email: str
    phone_number: str
    role: Optional[str] = None
    hire_date: Optional[datetime] = None
    is_active: bool
