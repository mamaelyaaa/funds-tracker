from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column

if TYPE_CHECKING:
    from . import (
        AccountModel,
        GoalModel,
        FundModel,
    )

from .base import Base
from .mixin import TimeStampMixin


class UserModel(Base, TimeStampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(31))
    password: Mapped[str]

    # Отношения
    accounts: Mapped[list["AccountModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    goals: Mapped[list["GoalModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    funds: Mapped[list["FundModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
