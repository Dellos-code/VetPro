from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "sqlite:///./vetpro.db"
    APP_TITLE: str = "VetPro"
    APP_VERSION: str = "1.0.0"


settings = Settings()
