"""update unique constraint in usersession

Revision ID: 4ff31bb6444b
Revises: f20fe7c87b69
Create Date: 2026-03-20 18:33:42.124807

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4ff31bb6444b"
down_revision: Union[str, Sequence[str], None] = "f20fe7c87b69"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f("ix_user_sessions_fingerprint"), table_name="user_sessions")
    op.create_index(
        op.f("ix_user_sessions_fingerprint"),
        "user_sessions",
        ["fingerprint"],
        unique=False,
    )
    op.create_unique_constraint(
        "session_user_fingerprint_constraint",
        "user_sessions",
        ["fingerprint", "user_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "session_user_fingerprint_constraint", "user_sessions", type_="unique"
    )
    op.drop_index(op.f("ix_user_sessions_fingerprint"), table_name="user_sessions")
    op.create_index(
        op.f("ix_user_sessions_fingerprint"),
        "user_sessions",
        ["fingerprint"],
        unique=True,
    )
