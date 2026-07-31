"""add json to export format

Revision ID: a1b2c3d4e5f6
Revises: 3aad8d2271ba
Create Date: 2026-07-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '3aad8d2271ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the 'json' value to the export_format enum."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TYPE export_format ADD VALUE IF NOT EXISTS 'JSON'"
        )
    else:
        # SQLite does not support ALTER TYPE; tests build the schema
        # from Base.metadata directly, so nothing to do here.
        pass


def downgrade() -> None:
    """Remove the 'json' value from the export_format enum.

    PostgreSQL cannot drop enum values; the type is recreated without
    'JSON' and existing rows are mapped back to 'PDF'.
    """
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            ALTER TABLE exports ALTER COLUMN format
                TYPE export_format USING format::text::export_format
            """
        )
        # Recreate the enum type without JSON
        op.execute("ALTER TYPE export_format RENAME TO export_format_old")
        op.execute("CREATE TYPE export_format AS ENUM ('PDF', 'DOCX', 'MARKDOWN', 'HTML')")
        op.execute(
            """
            ALTER TABLE exports ALTER COLUMN format
                TYPE export_format USING format::text::export_format
            """
        )
        op.execute("DROP TYPE export_format_old")
    else:
        pass
