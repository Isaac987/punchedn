from pathlib import Path
from fastapi import FastAPI
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Environment details
    env_file = Path(__file__).resolve().parent.parent / ".env"

    # App details
    app_name: str = "PunchedN"
    admin_email: str
    debug: bool = False

    # Database settings
    mongo_db_user: str
    mongo_db_password: SecretStr
    mongo_db_cluster: str
    mongo_db_app_name: str

    @property
    def mongo_db_url(self) -> str:
        return f"mongodb+srv://{self.mongo_db_user}:{self.mongo_db_password}@{self.mongo_db_host}/?appName={self.mongo_db_app_name}"

    model_config = SettingsConfigDict(env_file=env_file)


settings = Settings()
