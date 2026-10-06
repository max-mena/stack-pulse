"""Runtime configuration loaded from environment variables or a local `.env` file."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    github_token: SecretStr
    stackexchange_key: SecretStr
    gcp_project_id: str
    bq_location: str = "US"
    bq_raw_dataset: str = "raw"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # values come from the environment
