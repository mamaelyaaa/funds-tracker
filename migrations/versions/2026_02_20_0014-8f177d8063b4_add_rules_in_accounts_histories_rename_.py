"""add rules in accounts, histories, rename history

Revision ID: 8f177d8063b4
Revises: e6824971ae2b
Create Date: 2026-02-20 00:14:56.430324

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8f177d8063b4"
down_revision: Union[str, Sequence[str], None] = "e6824971ae2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "accounts_history",
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column("balance", sa.Float(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("balance >= 0", name="history_balance_gt_0"),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name="fk_savings_acc_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("savings_history")
    op.create_check_constraint("account_balance_gt_0", "accounts", "balance >= 0")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "savings_history",
        sa.Column("id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("account_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "balance",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name=op.f("fk_savings_acc_id"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("savings_history_pkey")),
    )
    op.drop_table("accounts_history")
    op.drop_constraint("account_balance_gt_0", "accounts", type_="check")
