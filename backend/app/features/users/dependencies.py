from typing import Annotated, Any, Dict

from core.security import verify_jwt
from fastapi import Depends, HTTPException, Security, status

from .repository import UserRepository
from .schemas import UserRead


async def get_current_user(
    payload: Annotated[
        Dict[str, Any],
        Security(verify_jwt),
    ],
    repository: Annotated[UserRepository, Depends(UserRepository)],
) -> UserRead:
    # Use get rather than [] for missing key validation
    # TODO: Create a payload object and validate members before getting to this point
    logto_id = payload.get("sub")

    if not logto_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    user_model = await repository.get_by_auth_id(logto_id)

    return UserRead.model_validate(user_model)
