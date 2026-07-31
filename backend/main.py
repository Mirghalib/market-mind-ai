"""Market Mind AI — backend entrypoint.

Run locally:
    uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.middleware.request_context import RequestContextMiddleware


def create_app() -> FastAPI:
    """Application factory. Imported here so uvicorn (and gunicorn
    workers) always get a fresh, fully-wired app instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs" if settings.ENV != "production" else None,
        redoc_url=None,
    )

    app.add_middleware(RequestContextMiddleware)
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        return {"message": f"{settings.APP_NAME} API is running"}

    return app


app = create_app()
