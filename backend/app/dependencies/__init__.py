"""Reusable FastAPI dependencies.

FastAPI sub-dependencies, exposed as callables:

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        ...
"""
