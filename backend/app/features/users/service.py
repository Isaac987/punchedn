from typing import Annotated

import structlog
from core.security import LogtoAPIClient, get_logto_api_client
from fastapi import Depends, HTTPException, status

from .models import UserModel
from .repository import UserRepository
from .schemas import UserCreate, UserResponse

_logger = structlog.get_logger()


class UserService:
    def __init__(
        self,
        repository: Annotated[UserRepository, Depends(UserRepository)],
        logto_client: Annotated[LogtoAPIClient, Depends(get_logto_api_client)],
    ):
        self._repository = repository
        self._logto_client = logto_client

    async def create_user(self, user: UserCreate) -> UserResponse:

        # Check if email and username are available before calling Logto
        # TODO: Add check for username
        existing_user = await self._repository.get_by_email(user.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists.",
            )

        auth_id = await self._logto_client.create_user(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        user_model = UserModel(**user.model_dump(), auth_id=auth_id)

        await self._repository.create(user_model)

        return UserResponse.model_validate(user_model)
