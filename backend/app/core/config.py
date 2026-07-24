from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends
from pydantic import Field, HttpUrl, SecretStr, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    # App details
    app_env: Literal["development", "testing", "production"] = Field(
        default="development"
    )
    app_name: str = "PunchedN"
    app_description: str = (
        "API to assist with employee scheduling, and shift management."
    )
    app_version: str = "v1"
    app_docs_url: str = "/docs"
    app_redoc_url: str = "/redoc"

    # Log settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = (
        "DEBUG" if app_env == "development" else "INFO"
    )
    # log_json: bool = app_env != "development"
    log_json: bool = False

    # Database settings
    mongo_user: str = Field(default="")
    mongo_password: SecretStr = Field(default=SecretStr(""))
    mongo_host: str = Field(default="")
    mongo_name: str = Field(default="")
    database_name: str = Field(default="")

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

    # Logto Settings
    logto_uri: HttpUrl
    logto_admin_app_id: str = Field(default="")
    logto_admin_app_secret: SecretStr = Field(default=SecretStr(""))

    @computed_field
    @property
    def logto_jwt_uri(self) -> str:
        return f"{self.logto_uri}oidc/jwks"

    @computed_field
    @property
    def logto_issuer_uri(self) -> str:
        return f"{self.logto_uri}oidc"

    logto_audience_uri: str = "https://dev.punchedn.com/api"

    model_config = SettingsConfigDict(
        env_file=_ENV_PATH,
        extra="ignore",
        env_ignore_empty=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


AppSettings = Annotated[Settings, Depends(get_settings)]
