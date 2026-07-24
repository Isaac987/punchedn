from typing import Any, Dict, Sequence

import structlog
from beanie import Document, init_beanie  # type: ignore
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError
from tenacity import AsyncRetrying, Retrying, stop_after_attempt, wait_exponential

from core.config import get_settings

_settings = get_settings()
_logger = structlog.get_logger(__name__)


class DatabaseManager:
    def __init__(
        self,
        mongo_uri: str,
        database_name: str,
        min_pool: int = 10,
        max_pool: int = 100,
    ):
        # Using the recommended type
        # Ref: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/mongoclient/#:~:text=client%3A%20AsyncMongoClient%5BDict%5Bstr%2C%20Any%5D%5D%20%3D%20AsyncMongoClient()
        self._client: AsyncMongoClient[Dict[str, Any]]
        self._mongo_uri: str = mongo_uri
        self._database_name: str = database_name
        self._min_pool: int = min_pool
        self._max_pool: int = max_pool

    async def connect(
        self, models: Sequence[type[Document]], retry_connection: int = 5
    ):
        """
        Initializes the AsyncMongoClient and registers all data models with Beanie.
        """
        _logger.info(
            "mongodb_connection_starting",
            database_name=_settings.database_name,
        )

        try:
            # Try to connect to the database retry_connections times
            for attempt in Retrying(
                stop=stop_after_attempt(retry_connection),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                reraise=True,
            ):
                with attempt:
                    self._client = AsyncMongoClient(
                        self._mongo_uri,
                        minPoolSize=self._min_pool,
                        maxPoolSize=self._max_pool,
                    )

            # Try to ping the db and try to connect in different ways?
            # Maybe we have a backup in the future.
            # For now, just raise an error
            # TODO: Try more things to get this db connected
            if not await self.get_health():
                raise ConnectionError

            # Initalize beanie with document models & get/create the database
            await init_beanie(self._client[self._database_name], document_models=models)

            _logger.info("db_connection_successful")

        except ConnectionError as e:
            # We only catch this error to log it
            # We want the server to crash if this fails
            # TODO: Raise a custom exception
            _logger.error(
                "db_connection_failed",
                error=str(e),
                retried_times=retry_connection,
                exc_info=True,
            )
            raise e

    async def disconnect(self):
        await self._client.close()

    async def get_health(self, retry_ping: int = 3) -> bool:
        """
        Trys to ping the database retry_ping number of times.
        This does not raise an exception, but signals the database is not responding.
        """
        status: bool = True

        try:
            # Try to ping the server retry_ping number of times
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(retry_ping),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                reraise=True,
            ):
                with attempt:
                    await self._client.admin.command("ping")
        except PyMongoError as e:
            _logger.error("db_not_responding", error=str(e), retried_times=retry_ping)
            status = False

        return status


# Create a single instance of our database manager to be used by the application
# One client can handle multiple requests at once
databaseManager = DatabaseManager(_settings.mongo_uri, _settings.database_name)
