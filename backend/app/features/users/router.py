from typing import Annotated, List

from beanie import PydanticObjectId
from fastapi import APIRouter, Body, Depends, Path, Query, status
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from .schemas import UserBase, UserCreate, UserResponse, UserUpdate
from .service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_one(
    user: Annotated[
        UserCreate,
        Body(
            description="The user payload containing required fields to create a new account."
        ),
    ],
    service: Annotated[UserService, Depends(UserService)],
) -> UserResponse:
    """
    Creates a new user.
    """
    return await service.create_user(user)


@router.get("/me", status_code=status.HTTP_200_OK)
def get_me() -> UserResponse:
    """
    Retrieves the profile of the currently authenticated user.
    """
    ...


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_by_id(
    user_id: Annotated[
        PydanticObjectId,
        Path(description="The unique MongoDB/database identifier of the user."),
    ],
) -> UserResponse:
    """
    Retrieves a specific user by their unique database ID.
    """
    ...


@router.get("/email/{user_email}", status_code=status.HTTP_200_OK)
def get_by_email(
    user_email: Annotated[
        EmailStr, Path(description="The exact email address of the user to retrieve.")
    ],
) -> UserResponse:
    """
    Retrieves a user by their email address.
    """
    ...


@router.get("/auth/{auth_id}", status_code=status.HTTP_200_OK)
def get_by_auth_id(
    auth_id: Annotated[
        str,
        Path(
            description="The unique ID provided by the external authentication provider (e.g., Auth0, Firebase)."
        ),
    ],
) -> UserResponse:
    """
    Retrieves a user by their external authentication provider ID.
    """
    ...


@router.get("", status_code=status.HTTP_200_OK)
def get_all(
    in_active: Annotated[
        bool,
        Query(
            description="If true, includes deactivated employees in the returned list."
        ),
    ] = False,
) -> List[UserBase]:
    """
    Returns a list of all active employees.
    """
    return MOCK_USERS


@router.patch("/{user_id}", status_code=status.HTTP_200_OK)
def update(
    user_id: Annotated[
        PydanticObjectId,
        Path(description="The unique database identifier of the user to update."),
    ],
    user: Annotated[
        UserUpdate,
        Body(
            description="The fields to update. Only the provided fields will be modified."
        ),
    ],
) -> UserResponse:
    """
    Partially updates specific fields of an existing user's profile.
    """
    ...


@router.patch("/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
def deactivate(
    user_id: Annotated[
        PydanticObjectId,
        Path(description="The unique database identifier of the user to deactivate."),
    ],
) -> None:
    """
    Deactivates a user account without permanently deleting the record.
    """
    ...
