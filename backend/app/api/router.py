"""API v1 router aggregator.

New feature routers get mounted here:

    from app.api.endpoints.users import router as users_router
    api_router.include_router(users_router, prefix="/users", tags=["users"])
"""
from fastapi import APIRouter

from app.api.endpoints.health import router as health_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
