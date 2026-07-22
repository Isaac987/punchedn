from typing import Annotated, Any, Dict

from core.security import verify_jwt
from fastapi import Depends, HTTPException, Security, status

from .models import UserModel
from .repository import UserRepository


async def get_current_user(
    payload: Annotated[
        Dict[str, Any],
        Security(verify_jwt),
    ],
    repository: Annotated[UserRepository, Depends(UserRepository)],
) -> UserModel:
    """
    Validates the JWT token, enforces permission scopes, and returns the UserModel.
    """
    # Use get rather than [] for missing key validation
    # TODO: Create a payload object and validate members before getting to this point
    auth_id = payload.get("sub")

    if not auth_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    user_model = await repository.get_by_auth_id(auth_id)

    return user_model
