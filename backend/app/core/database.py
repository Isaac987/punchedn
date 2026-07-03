from typing import Annotated
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError
from tenacity import retry, stop_after_attempt, wait_exponential
from core.config import Settings, get_settings, settings_dependency

_client: AsyncMongoClient


@retry(
    stop=stop_after_attempt(get_settings().mongo_ping_attempts),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
async def _ping(client: AsyncMongoClient):
    await client.admin.command("ping")


async def connect_to_mongo(settings: settings_dependency) -> None:
    global _client

    _client = AsyncMongoClient(
        settings.mongo_uri,
        minPoolSize=settings.mongo_min_pool_size,
        maxPoolSize=settings.mongo_max_pool_size,
    )

    try:
        await _ping(_client)
    except PyMongoError:
        pass
        # TODO: Log the error


async def disconnect_from_mongo() -> None:
    await _client.close()


async def get_client() -> AsyncMongoClient:
     return _client
