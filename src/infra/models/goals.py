from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    String,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.accounts.values import Title
from domain.goals.values import GoalStatus

if TYPE_CHECKING:
    from . import UserModel

from .base import Base
from .mixin import CreatedAtMixin


class GoalModel(Base, CreatedAtMixin):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("target_amount >= 0", name="target_ge_0"),
        CheckConstraint("current_amount >= 0", name="current_ge_0"),
        UniqueConstraint("user_id", "title", name="uq_goals_user_id_title"),
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(Title.MAX_LEN))
    target_amount: Mapped[float]
    current_amount: Mapped[float]
    status: Mapped[GoalStatus]
    deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Отношения
    user: Mapped["UserModel"] = relationship(backref="goals")
