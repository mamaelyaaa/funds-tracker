"""update user table

Revision ID: b593c471ba63
Revises: b676e0138035
Create Date: 2026-03-19 16:36:16.326804

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b593c471ba63"
down_revision: Union[str, Sequence[str], None] = "b676e0138035"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("username", sa.String(length=31), nullable=False))
    op.add_column("users", sa.Column("password", sa.String(), nullable=False))
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.drop_column("users", "name")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "users",
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.drop_column("users", "updated_at")
    op.drop_column("users", "password")
    op.drop_column("users", "username")
