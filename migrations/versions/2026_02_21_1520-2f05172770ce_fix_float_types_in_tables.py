"""fix float types in tables

Revision ID: 2f05172770ce
Revises: 8f177d8063b4
Create Date: 2026-02-21 15:20:49.576671

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2f05172770ce"
down_revision: Union[str, Sequence[str], None] = "8f177d8063b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "accounts_history",
        sa.Column("delta", sa.Numeric(scale=2), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("accounts_history", "delta")
