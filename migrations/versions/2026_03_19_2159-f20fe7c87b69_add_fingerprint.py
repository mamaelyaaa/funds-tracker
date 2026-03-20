"""add fingerprint

Revision ID: f20fe7c87b69
Revises: f171f40b17a5
Create Date: 2026-03-19 21:59:38.001650

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f20fe7c87b69"
down_revision: Union[str, Sequence[str], None] = "f171f40b17a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user_sessions", sa.Column("fingerprint", sa.String(), nullable=False)
    )
    op.create_index(
        op.f("ix_user_sessions_fingerprint"),
        "user_sessions",
        ["fingerprint"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_user_sessions_fingerprint"), table_name="user_sessions")
    op.drop_column("user_sessions", "fingerprint")
