"""add users

Revision ID: 4e3863660ca2
Revises:
Create Date: 2026-01-29 01:24:07.330474

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4e3863660ca2"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
