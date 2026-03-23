"""add fund model

Revision ID: d667e13dfe57
Revises: c822ec2e8872
Create Date: 2026-03-01 16:44:04.170383

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d667e13dfe57"
down_revision: Union[str, Sequence[str], None] = "c822ec2e8872"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "funds",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("OPEN", "CLOSED", "DISTRIBUTED", name="fundstatus"),
            nullable=False,
        ),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("start_date <= end_date", name="fund_date_validation"),
        sa.CheckConstraint("total_amount >= 0", name="fund_total_amount_ge_0"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "start_date", name="uc_user_id_start_date"),
    )
    op.create_index(
        "idx_user_id_start_date",
        "funds",
        ["user_id", "start_date"],
        unique=False,
    )
    op.create_index(op.f("ix_funds_user_id"), "funds", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_funds_user_id"), table_name="funds")
    op.drop_index("idx_user_id_start_date", table_name="funds")
    op.drop_table("funds")
    op.execute("DROP TYPE fundstatus")
