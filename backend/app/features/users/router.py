from typing import List

from fastapi import APIRouter
from pydantic_extra_types.phone_numbers import PhoneNumber

from .schemas import UserBase, UserRead

router = APIRouter(prefix="/users", tags=["Users"])

MOCK_USERS: List[UserBase] = [
    UserBase(
        first_name="Alice",
        last_name="Smith",
        email="alice.smith@example.com",
        phone_number=PhoneNumber("+12025550101"),
    ),
    UserBase(
        first_name="Bob",
        last_name="Jones",
        email="bob.jones@example.com",
        phone_number=PhoneNumber("+12025550102"),
    ),
    UserBase(
        first_name="Charlie",
        last_name="Brown",
        email="charlie.b@example.com",
        phone_number=PhoneNumber("+12025550103"),
    ),
    UserBase(
        first_name="Diana",
        last_name="Prince",
        email="diana.prince@example.com",
        phone_number=PhoneNumber("+12025550104"),
    ),
    UserBase(
        first_name="Evan",
        last_name="Wright",
        email="evan.w@example.com",
        phone_number=PhoneNumber("+12025550105"),
    ),
]


@router.get("", response_model=List[UserBase])
def get_all_users():
    """Returns a list of all active employees."""
    return MOCK_USERS
