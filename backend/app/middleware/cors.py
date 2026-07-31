"""CORS configuration helper.

FastAPI's CORSMiddleware reads settings at import time. This wrapper
builds it from the application settings so origins, methods and headers
are driven by configuration rather than hard-coded in main.py.
"""
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from app.core.config import settings


def create_cors_middleware() -> type[CORSMiddleware]:
    """Return a CORSMiddleware subclass configured from settings."""
    middleware_cls = CORSMiddleware

    class SettingsCORSMiddleware(middleware_cls):  # type: ignore[misc]
        def __init__(self, app: ASGIApp) -> None:
            super().__init__(
                app=app,
                allow_origins=settings.CORS_ORIGINS,
                allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
                allow_methods=settings.CORS_ALLOW_METHODS,
                allow_headers=settings.CORS_ALLOW_HEADERS,
            )

    return SettingsCORSMiddleware
