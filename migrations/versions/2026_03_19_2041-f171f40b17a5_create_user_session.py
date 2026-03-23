"""create user session

Revision ID: f171f40b17a5
Revises: b593c471ba63
Create Date: 2026-03-19 20:41:42.093525

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f171f40b17a5"
down_revision: Union[str, Sequence[str], None] = "b593c471ba63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("refresh_jti", sa.String(), nullable=False),
        sa.Column("expires_in", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("created_at <= expires_in", name="session_date_constraint"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_us_user_id", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("refresh_jti"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_sessions")
