from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, Index, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.funds.values import FundStatus
from infra.models import Base

if TYPE_CHECKING:
    from . import UserModel

from infra.models.mixin import CreatedAtMixin


class FundModel(Base, CreatedAtMixin):
    __tablename__ = "funds"
    __table_args__ = (
        UniqueConstraint("user_id", "start_date", name="uc_user_id_start_date"),
        Index("idx_user_id_start_date", "user_id", "start_date"),
        CheckConstraint("total_amount >= 0", name="fund_total_amount_ge_0"),
        CheckConstraint("start_date <= end_date", name="fund_date_validation"),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    total_amount: Mapped[float]
    status: Mapped[FundStatus] = mapped_column(default=FundStatus.OPEN)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Отношения
    user: Mapped["UserModel"] = relationship(back_populates="funds")
