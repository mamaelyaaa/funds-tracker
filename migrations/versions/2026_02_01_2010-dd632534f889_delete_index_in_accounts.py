"""delete index in accounts

Revision ID: dd632534f889
Revises: 2ed26f640a85
Create Date: 2026-02-01 20:10:35.750302

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dd632534f889"
down_revision: Union[str, Sequence[str], None] = "2ed26f640a85"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f("fk_acc_user_id"), "accounts", type_="foreignkey")
    op.create_foreign_key(
        "fk_acc_user_id",
        "accounts",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(op.f("fk_savings_acc_id"), "savings_history", type_="foreignkey")
    op.create_foreign_key(
        "fk_savings_acc_id",
        "savings_history",
        "accounts",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_savings_acc_id", "savings_history", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_savings_acc_id"),
        "savings_history",
        "accounts",
        ["account_id"],
        ["id"],
    )
    op.drop_constraint("fk_acc_user_id", "accounts", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_acc_user_id"), "accounts", "users", ["user_id"], ["id"]
    )
