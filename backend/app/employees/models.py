from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, StrictBool, Field
from typing import List, Annotated
from datetime import datetime

class Employee(Document):
    auth_id: Annotated[str, Indexed(unique=True)]
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    role: str
    hire_date: datetime | None = None
    pay_rate: float | None = Field(default=None, ge=0)
    max_hours: float = Field(gt=0)
    max_hours_term: str
    is_active: StrictBool
    trained_skills: List[str] = Field(default_factory=list)
    class Settings:
        collection_name="Employees"

class EmployeeCreate(BaseModel):
    auth_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    role: str
    hire_date: datetime | None = None
    pay_rate: float | None = Field(default=None, ge=0)
    max_hours: float = Field(gt=0)
    max_hours_term: str
    is_active: StrictBool
    trained_skills: List[str] = Field(default_factory=list)

# class EmployeeUpdate(BaseModel):