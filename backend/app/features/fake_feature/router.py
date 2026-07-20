from typing import Annotated, Any, Dict

from core.permissions import UserPermissions
from core.security import verify_jwt
from fastapi import APIRouter, Security

router = APIRouter(prefix="/fake_feature", tags=["Fake Feature"])


@router.get("/locked_route")
def locked_route(
    _payload: Annotated[
        Dict[str, Any],
        Security(verify_jwt, scopes=[UserPermissions.READ, UserPermissions.WRITE]),
    ],
):
    return _payload
