"""update goal model

Revision ID: c822ec2e8872
Revises: 6de8dc4e5f0b
Create Date: 2026-02-26 18:25:16.793594

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c822ec2e8872"
down_revision: Union[str, Sequence[str], None] = "6de8dc4e5f0b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f("goals_account_id_fkey"), "goals", type_="foreignkey")
    op.drop_column("goals", "account_id")
    op.drop_column("goals", "savings_percentage")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "goals",
        sa.Column(
            "savings_percentage",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "goals",
        sa.Column("account_id", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        op.f("goals_account_id_fkey"),
        "goals",
        "accounts",
        ["account_id"],
        ["id"],
    )
