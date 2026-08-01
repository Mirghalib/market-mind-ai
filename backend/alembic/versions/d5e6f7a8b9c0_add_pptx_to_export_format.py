"""add pptx to export format

Revision ID: d5e6f7a8b9c0
Revises: c3d4e5f6a7b8
Create Date: 2026-08-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd5e6f7a8b9c0'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the 'PPTX' value to the export_format enum."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TYPE export_format ADD VALUE IF NOT EXISTS 'PPTX'"
        )
    else:
        # SQLite does not support ALTER TYPE; tests build the schema
        # from Base.metadata directly, so nothing to do here.
        pass


def downgrade() -> None:
    """Remove the 'PPTX' value from the export_format enum.

    PostgreSQL cannot drop enum values; the type is recreated without
    'PPTX' and existing rows are mapped back to 'PDF'.
    """
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            ALTER TABLE exports ALTER COLUMN format
                TYPE export_format USING format::text::export_format
            """
        )
        op.execute("ALTER TYPE export_format RENAME TO export_format_old")
        op.execute(
            "CREATE TYPE export_format AS ENUM ('PDF', 'DOCX', 'MARKDOWN', 'HTML', 'JSON')"
        )
        op.execute(
            """
            ALTER TABLE exports ALTER COLUMN format
                TYPE export_format USING format::text::export_format
            """
        )
        op.execute("DROP TYPE export_format_old")
    else:
        pass
