"""API v1 router aggregator.

New feature routers get mounted here:

    from app.api.endpoints.users import router as users_router
    api_router.include_router(users_router, prefix="/users", tags=["users"])
"""
from fastapi import APIRouter

from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.export import router as export_router
from app.api.endpoints.generate import router as generate_router
from app.api.endpoints.generation_history import router as generation_history_router
from app.api.endpoints.health import router as health_router
from app.api.endpoints.user import router as user_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(generate_router, tags=["generate"])
api_router.include_router(export_router, tags=["export"])
api_router.include_router(
    generation_history_router,
    prefix="/generation-history",
    tags=["generation-history"],
)
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(user_router, prefix="/dashboard", tags=["dashboard"])
