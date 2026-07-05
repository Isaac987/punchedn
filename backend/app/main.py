from contextlib import asynccontextmanager

import structlog
from core.config import AppSettings, get_settings
from core.database import connect_to_mongo, disconnect_from_mongo
from core.logger import configure_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.logging_middleware import LoggingMiddleware

_settings: AppSettings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(_settings)

    logger = structlog.get_logger(__name__)
    logger.info("Application Starting")

    await connect_to_mongo(get_settings())

    yield

    await disconnect_from_mongo()
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
