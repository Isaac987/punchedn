from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from core.config import AppSettings

_client: AsyncMongoClient


# @retry(
#     stop=stop_after_attempt(settings.mongo_ping_attempts),
#     wait=wait_exponential(multiplier=1, min=1, max=10),
#     reraise=True,
# )
# async def _ping(client: AsyncMongoClient, settings: AppSettings):
#     await client.admin.command("ping")


async def _ping(client: AsyncMongoClient, retry: int = 1):
    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(retry),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    ):
        with attempt:
            await client.admin.command("ping")


async def connect_to_mongo(settings: AppSettings) -> None:
    global _client

    _client = AsyncMongoClient(
        settings.mongo_uri,
        minPoolSize=settings.mongo_min_pool_size,
        maxPoolSize=settings.mongo_max_pool_size,
    )

    try:
        await _ping(_client, retry=settings.mongo_ping_attempts)
    except PyMongoError:
        pass
        # TODO: Log the error


async def disconnect_from_mongo() -> None:
    await _client.close()


async def get_client() -> AsyncMongoClient:
    return _client
