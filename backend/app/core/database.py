from typing import Any, Sequence

import structlog
from beanie import Document, init_beanie
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from core.config import AppSettings

_logger = structlog.get_logger(__name__)
_client: AsyncMongoClient[dict[str, Any]] | None = None


async def _ping(client: AsyncMongoClient[dict[str, Any]], retry: int = 1):
    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(retry),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    ):
        with attempt:
            await client.admin.command("ping")


async def connect_to_mongo(
    settings: AppSettings, document_models: Sequence[type[Document]]
) -> None:
    global _client

    _client = AsyncMongoClient(
        settings.mongo_uri,
        minPoolSize=settings.mongo_min_pool_size,
        maxPoolSize=settings.mongo_max_pool_size,
    )

    try:
        await _ping(_client, retry=settings.mongo_ping_attempts)
    except PyMongoError:
        _logger.exception("mongo_connection_failed")
        raise

    # TODO: Define db name in settings
    await init_beanie(database=_client["PunchedN"], document_models=document_models)


async def disconnect_from_mongo() -> None:
    if _client:
        await _client.close()


async def get_client() -> AsyncMongoClient[dict[str, Any]]:
    if _client is None:
        raise RuntimeError(
            "Mongo client not initialized — call connect_to_mongo() first"
        )

    return _client


async def health_check() -> bool:
    status: bool = False

    if _client is not None:
        try:
            await _client.admin.command("ping")
            status = True
        except Exception:
            _logger.exception("readiness_check_failed")

    return status
