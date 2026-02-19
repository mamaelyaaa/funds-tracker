"""create goal table

Revision ID: e6824971ae2b
Revises: dd632534f889
Create Date: 2026-02-17 15:47:16.377791

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e6824971ae2b"
down_revision: Union[str, Sequence[str], None] = "dd632534f889"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "goals",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("account_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(length=63), nullable=False),
        sa.Column("target_amount", sa.Float(), nullable=False),
        sa.Column("current_amount", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "COMPLETED", "FAILED", "ARCHIVED", name="goalstatus"),
            nullable=False,
        ),
        sa.Column("savings_percentage", sa.Float(), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("current_amount >= 0", name="current_ge_0"),
        sa.CheckConstraint("target_amount >= 0", name="target_ge_0"),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "title", name="uq_goals_user_id_title"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("goals")
    op.execute("DROP TYPE goalstatus")
