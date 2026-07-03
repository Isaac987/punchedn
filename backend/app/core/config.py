from pathlib import Path
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):

    # App details
    app_name: str = "PunchedN"
    app_description: str = (
        "API to assist with employee scheduling, and shift management."
    )
    app_version: str = "v1"
    app_docs_url: str = "/docs"
    app_redoc_url: str = "/redoc"
    admin_email: str
    debug: bool = False

    # Database settings
    mongo_user: str
    mongo_password: SecretStr
    mongo_host: str
    mongo_name: str
    mongo_min_pool_size: int = 10
    mongo_max_pool_size: int = 100
    mongo_ping_attempts: int = 5

    @property
    def mongo_uri(self) -> str:
        return f"mongodb+srv://{self.mongo_user}:{self.mongo_password.get_secret_value()}@{self.mongo_host}/?appName={self.mongo_name}"


    # Load settings from .env
    model_config = SettingsConfigDict(env_file=_ENV_PATH)


# We are handling settings like this so we can test other settings via dependency injection.
# lru_cache will only create the settings object once, so there is not a constant need to read the .env file.
# https://fastapi.tiangolo.com/advanced/settings/?h=sett#creating-the-settings-only-once-with-lru-cache
@lru_cache
def get_settings() -> Settings:
    return Settings()

settings_dependency = Annotated[Settings, Depends(get_settings)]
