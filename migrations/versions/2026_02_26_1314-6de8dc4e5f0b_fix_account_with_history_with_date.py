"""fix account with history with date

Revision ID: 6de8dc4e5f0b
Revises: 2f05172770ce
Create Date: 2026-02-26 13:14:23.123363

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6de8dc4e5f0b"
down_revision: Union[str, Sequence[str], None] = "2f05172770ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "accounts",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "accounts_history",
        sa.Column(
            "is_monthly_closing", sa.Boolean(), nullable=False, server_default="False"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("accounts_history", "is_monthly_closing")
    op.drop_column("accounts", "updated_at")
