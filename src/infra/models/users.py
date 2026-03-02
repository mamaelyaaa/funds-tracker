from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from . import AccountModel, GoalModel

from .base import Base
from .mixin import CreatedAtMixin


class UserModel(Base, CreatedAtMixin):
    __tablename__ = "users"

    name: Mapped[str]

    accounts: Mapped[list["AccountModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        single_parent=True,
    )
    goals: Mapped[list["GoalModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
