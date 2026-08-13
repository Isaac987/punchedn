from typing import Annotated, Any, Dict, List

from beanie import PydanticObjectId
from fastapi import APIRouter, Body, Depends, Path, Query, Security, status
from pydantic import EmailStr

from core.security import verify_jwt
from core.permissions import UserPermissions

from .schemas import UserBase, UserCreate, UserResponse, UserUpdate
from .service import UserService
from .dependencies import get_current_user
from .models import UserModel

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
def get_me(user: Annotated[UserModel, Depends(get_current_user)]) -> UserResponse:
    """
    Retrieves the profile of the currently authenticated user.
    """
    return user


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_by_id(
    user_id: Annotated[
        PydanticObjectId,
        Path(description="The unique MongoDB/database identifier of the user."),
    ],
    service: Annotated[UserService, Depends(UserService)],
    _payload: Annotated[
        Dict[str, Any],
        Security(verify_jwt, scopes=[UserPermissions.READ]),
    ],
) -> UserResponse:
    """
    Retrieves a specific user by their unique database ID.
    """
    return await service.get_by_id(user_id)


@router.get("/email/{user_email}", status_code=status.HTTP_200_OK)
async def get_by_email(
    user_email: Annotated[
        EmailStr, Path(description="The exact email address of the user to retrieve.")
    ],
    service: Annotated[UserService, Depends(UserService)],
    _payload: Annotated[
        Dict[str, Any],
        Security(verify_jwt, scopes=[UserPermissions.READ]),
    ],
) -> UserResponse:
    """
    Retrieves a user by their email address.
    """
    return await service.get_by_email(user_email)


@router.get("/auth/{auth_id}", status_code=status.HTTP_200_OK)
async def get_by_auth_id(
    auth_id: Annotated[
        str,
        Path(
            description="The unique ID provided by the external authentication provider (e.g., Logto, Auth0)."
        ),
    ],
    service: Annotated[UserService, Depends(UserService)],
    _payload: Annotated[
        Dict[str, Any],
        Security(verify_jwt, scopes=[UserPermissions.READ]),
    ],
) -> UserResponse:
    """
    Retrieves a user by their external authentication provider ID.
    """
    return await service.get_by_auth_id(auth_id)


@router.get("/all/", status_code=status.HTTP_200_OK)
async def get_all(
    service: Annotated[UserService, Depends(UserService)],
    _payload: Annotated[
        Dict[str, Any],
        Security(verify_jwt, scopes=[UserPermissions.READ]),
    ],
    is_active: Annotated[
        bool,
        Query(description="If true, includes deactivated users in the returned list."),
    ] = False,
) -> List[UserResponse]:
    """
    Returns a list of all users.
    """
    return await service.get_all(is_active=is_active)


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
