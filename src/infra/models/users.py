from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from . import AccountModel

from .base import Base
from .mixin import DateMixin


class UserModel(Base, DateMixin):
    __tablename__ = "users"

    name: Mapped[str]

    accounts: Mapped[list["AccountModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        single_parent=True,
    )
