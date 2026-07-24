from contextlib import asynccontextmanager

import structlog
from api.router import api_router
from core.config import AppSettings, get_settings
from core.database import databaseManager
from core.logger import configure_logging
from core.security import LogtoAPIClient, get_logto_api_client
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
_logto_client: LogtoAPIClient = get_logto_api_client()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(_settings.log_json, _settings.log_level)
    logger = structlog.get_logger(__name__)
    logger.info("Application Starting")

    # Connect to the database
    # Let any errors happen, we handle retry logic in the database manager
    # If it fails at this point, then we let the applicaiton DIE
    await databaseManager.connect(BEANIE_DOCUMENTS)
    _logto_client.connect()

    yield

    # Close the database connection
    await databaseManager.disconnect()
    await _logto_client.disconnect()


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
