from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from domain.funds.values import FundStatus
from infra.models import Base
from infra.models.mixin import CreatedAtMixin


class FundModel(Base, CreatedAtMixin):
    __tablename__ = "funds"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    total_amount: Mapped[float]
    status: Mapped[FundStatus] = mapped_column(default=FundStatus.OPEN)
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]

    __table_args__ = (
        UniqueConstraint("user_id", "start_date", name="uc_user_id_start_date"),
        Index("idx_user_id_start_date", "user_id", "start_date"),
        CheckConstraint("total_amount >= 0", name="fund_total_amount_ge_0"),
        CheckConstraint("start_date < end_date", name="fund_date_validation"),
    )
