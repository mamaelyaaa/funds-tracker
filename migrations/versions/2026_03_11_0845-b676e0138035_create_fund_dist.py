"""create fund dist

Revision ID: b676e0138035
Revises: 611b12c44806
Create Date: 2026-03-11 08:45:55.643649

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b676e0138035"
down_revision: Union[str, Sequence[str], None] = "611b12c44806"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "funds_distribution",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("fund_id", sa.String(), nullable=False),
        sa.Column("reserve_id", sa.String(), nullable=False),
        sa.Column(
            "reserve_type",
            sa.Enum("GOAL", "ACCOUNT", name="fundreservetype"),
            nullable=False,
        ),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("percent_applied", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "percent_applied >= 0 AND percent_applied <= 100",
            name="fund_dist_percent_constraint",
        ),
        sa.CheckConstraint("amount >= 0", name="fund_dist_amount_ge_0"),
        sa.ForeignKeyConstraint(
            ["fund_id"],
            ["funds.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "fund_id", "reserve_id", "reserve_type", name="uc_fund_dist"
        ),
    )
    op.alter_column(
        "funds",
        "start_date",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "funds",
        "end_date",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "funds",
        "end_date",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.alter_column(
        "funds",
        "start_date",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.drop_table("funds_distribution")
    op.execute("DROP TYPE IF EXISTS fundruletype")
    op.execute("DROP TYPE fundreservetype")
