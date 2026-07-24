from datetime import datetime
from typing import List

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone_number: PhoneNumber
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserResponse(UserBase):
    id: PydanticObjectId = Field(alias="_id")
    roles: List[str] = []
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class UserCreate(UserBase): ...


# This is different from the rest
# A patch may only update one field
class UserUpdate(BaseModel): ...
