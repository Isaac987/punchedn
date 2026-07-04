from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from pydantic import Field, SecretStr, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    # Production details
    debug: bool = False

    # App details
    app_name: str = "PunchedN"
    app_description: str = (
        "API to assist with employee scheduling, and shift management."
    )
    app_version: str = "v1"
    app_docs_url: str = "/docs"
    app_redoc_url: str = "/redoc"

    # Database settings
    mongo_user: str = Field(default=...)
    mongo_password: SecretStr = Field(default=...)
    mongo_host: str = Field(default=...)
    mongo_name: str = Field(default=...)
    mongo_min_pool_size: int = 10
    mongo_max_pool_size: int = 100
    mongo_ping_attempts: int = 5

    @computed_field
    @property
    def mongo_uri(self) -> str:
        url = MultiHostUrl.build(
            scheme="mongodb+srv",
            username=self.mongo_user,
            password=self.mongo_password.get_secret_value(),  # Still needed internally for building
            host=self.mongo_host,
            query=f"appName={self.mongo_name}",
        )

        return str(url)

    model_config = SettingsConfigDict(env_file=_ENV_PATH)


@lru_cache
def get_settings() -> Settings:
    return Settings()


AppSettings = Annotated[Settings, Depends(get_settings)]
