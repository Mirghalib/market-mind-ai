"""add profile_image to users

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-31 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add users.profile_image (relative path of the uploaded image)."""
    op.add_column(
        'users',
        sa.Column(
            'profile_image', sa.String(length=512), nullable=True,
            comment='Relative path of the profile image, e.g. uploads/profile_images/<uuid>.jpg',
        ),
    )


def downgrade() -> None:
    """Remove users.profile_image."""
    op.drop_column('users', 'profile_image')
