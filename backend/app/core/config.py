"""Application configuration.

Loads settings from environment variables / .env file via pydantic-settings.
Access anywhere with:

    from app.core.config import settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "Market Mind AI"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # --- Security ---
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # --- Database ---
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/market_mind_ai"
    )

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    @property
    def ENV(self) -> str:
        return self.APP_ENV

    # Aliases matching common conventions
    @property
    def PROJECT_NAME(self) -> str:
        return self.APP_NAME

    @property
    def VERSION(self) -> str:
        return self.APP_VERSION

    @property
    def DEBUG(self) -> bool:
        return self.APP_DEBUG


settings = Settings()
