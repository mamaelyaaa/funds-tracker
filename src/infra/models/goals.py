from datetime import datetime

from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from domain.goals.values import GoalStatus
from . import Base
from .mixin import DataMixin


class GoalModel(Base, DataMixin):
    __tablename__ = "goals"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"))

    title: Mapped[str] = mapped_column(String(63))
    target_amount: Mapped[float]
    current_amount: Mapped[float]

    status: Mapped[GoalStatus]
    savings_percentage: Mapped[float]
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("target_amount >= 0", name="target_ge_0"),
        CheckConstraint("current_amount >= 0", name="current_ge_0"),
        UniqueConstraint("user_id", "title", name="uq_goals_user_id_title"),
    )
