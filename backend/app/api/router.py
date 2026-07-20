from core.health import router as health_router
from fastapi import APIRouter
from features.fake_feature.router import router as fake_feature_router

api_router = APIRouter()

# Attach system routes
api_router.include_router(health_router)

# Attach feature routes
api_router.include_router(fake_feature_router)
