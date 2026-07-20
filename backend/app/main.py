from contextlib import asynccontextmanager

import structlog
from api.router import api_router
from core.config import AppSettings, get_settings
from core.database import connect_to_mongo, disconnect_from_mongo
from core.logger import configure_logging
from core.mongodb import close_connection, test_connection, test_db_connection
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the exported feature beanie documents
from features.users import feature_models as user_models
from middleware.logging_middleware import LoggingMiddleware

# Unpack every exported beanie document
BEANIE_DOCUMENTS = [
    *user_models,
]

_settings: AppSettings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(_settings)
    logger = structlog.get_logger(__name__)
    logger.info("Application Starting")
    try:
        await connect_to_mongo(_settings, BEANIE_DOCUMENTS)

    finally:
        await test_connection()
        await test_db_connection()
    yield

    try:
        await disconnect_from_mongo()
    finally:
        await close_connection()
        logger.info("Application shutting down")


app = FastAPI(
    title=_settings.app_name,
    description=_settings.app_description,
    version=_settings.app_version,
    docs_url=_settings.app_docs_url,
    redoc_url=_settings.app_redoc_url,
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware, exclude_paths={"/health", "/metrics"})

# TODO: Define a list of origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#     )
