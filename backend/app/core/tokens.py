"""Token helpers shared by the auth endpoints."""
from app.core.security import create_access_token
from app.models.user import User


def create_user_access_token(user: User) -> str:
    """Build a JWT for ``user`` carrying RBAC claims for the frontend.

    Claims:
        sub     - user id (primary claim, used for DB lookup)
        user_id - user id (frontend convenience)
        email   - user email (frontend convenience)
        role    - role name, e.g. "admin" / "user" (frontend routing)

    The backend never trusts these claims alone: get_current_user
    re-resolves the user and role from the database on every request.
    """
    return create_access_token(
        subject=user.id,
        extra_claims={
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role_name,
        },
    )
