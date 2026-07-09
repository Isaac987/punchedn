from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from core import database

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", status_code=status.HTTP_200_OK)
def liveness():
    return {"status": "healthy"}


@router.get("/ready")
async def readiness():
    checks = {}
    status_code = status.HTTP_200_OK

    if await database.health_check():
        checks["mongodb"] = "healthy"
    else:
        checks["mongodb"] = "healthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(status_code=status_code, content={"checks": checks})
