from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
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


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[PhoneNumber] = None
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @model_validator(mode="after")
    def at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for a PATCH update.")
        return self
