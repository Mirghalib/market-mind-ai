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
    # Session-mode pooler URL used by Alembic migrations (Supabase).
    # Falls back to DATABASE_URL when unset.
    DIRECT_URL: str | None = None

    @property
    def MIGRATION_URL(self) -> str:
        """URL used by Alembic.

        Prefers DIRECT_URL (session-mode pooler, safe for DDL). If it is
        a bare postgresql:// URL, normalize it to the asyncpg driver used
        by env.py; otherwise fall back to DATABASE_URL.
        """
        url = self.DIRECT_URL or self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # --- Uploads ---
    UPLOAD_DIR: str = "uploads"
    PROFILE_IMAGE_DIR: str = "uploads/profile_images"
    UPLOAD_MAX_SIZE: int = 5 * 1024 * 1024  # 5 MB
    PROFILE_IMAGE_ALLOWED_TYPES: dict[str, str] = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }
    PUBLIC_BASE_URL: str = "http://localhost:8000"

    # --- AI (LLM provider) ---
    AI_PROVIDER: str = "openai"
    AI_MODEL: str = "gpt-4o-mini"
    AI_API_KEY: str = ""  # set via env (OPENAI_API_KEY / ANTHROPIC_API_KEY)
    AI_MAX_TOKENS: int = 4096
    AI_TEMPERATURE: float = 0.2
    AI_RETRY_ATTEMPTS: int = 3
    AI_RETRY_BACKOFF_SECONDS: float = 1.0
    AI_REQUEST_TIMEOUT_SECONDS: float = 60.0

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
