from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
    Index,
    CheckConstraint,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.funds.values import FundStatus, FundRuleType
from . import Base

if TYPE_CHECKING:
    from . import UserModel

from infra.models.mixin import CreatedAtMixin


class FundModel(Base, CreatedAtMixin):
    __tablename__ = "funds"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    total_amount: Mapped[float]
    status: Mapped[FundStatus] = mapped_column(default=FundStatus.OPEN)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("user_id", "start_date", name="uc_user_id_start_date"),
        Index("idx_user_id_start_date", "user_id", "start_date"),
        CheckConstraint("total_amount >= 0", name="fund_total_amount_ge_0"),
        CheckConstraint("start_date <= end_date", name="fund_date_validation"),
    )

    # Отношения
    user: Mapped["UserModel"] = relationship(back_populates="funds")
    distributions: Mapped[list["FundDistributionModel"]] = relationship(
        back_populates="fund", cascade="all, delete-orphan"
    )


class FundDistributionModel(Base, CreatedAtMixin):
    __tablename__ = "funds_distribution"

    fund_id: Mapped[str] = mapped_column(ForeignKey("funds.id"))
    reserve_id: Mapped[str]
    reserve_type: Mapped[FundRuleType]
    amount: Mapped[float]
    percent_applied: Mapped[int]

    __table_args__ = (
        UniqueConstraint("fund_id", "reserve_id", "reserve_type", name="uc_fund_dist"),
        CheckConstraint("amount >= 0", name="fund_dist_amount_ge_0"),
        CheckConstraint(
            "percent_applied >= 0 AND percent_applied <= 100",
            name="fund_dist_percent_constraint",
        ),
    )

    fund: Mapped["FundModel"] = relationship(back_populates="distributions")
