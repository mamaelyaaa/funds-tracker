"""add accounts

Revision ID: 633655d3351a
Revises: 4e3863660ca2
Create Date: 2026-01-29 01:25:02.413049

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "633655d3351a"
down_revision: Union[str, Sequence[str], None] = "4e3863660ca2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("CARD", "INVESTMENT", "CASH", name="accounttype"),
            nullable=False,
        ),
        sa.Column("balance", sa.Float(), nullable=False),
        sa.Column(
            "currency",
            sa.Enum("RUB", "USD", name="accountcurrency"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_acc_user_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uc_user_id_with_name"),
    )
    op.create_index(op.f("ix_accounts_name"), "accounts", ["name"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_accounts_name"), table_name="accounts")
    op.drop_table("accounts")
    op.execute("DROP TYPE accounttype")
    op.execute("DROP TYPE accountcurrency")
