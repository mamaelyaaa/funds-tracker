from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from infra.models import AccountModel

from infra.models.base import Base
from infra.models.mixin import DataMixin


class UserModel(Base, DataMixin):
    __tablename__ = "users"

    name: Mapped[str]

    accounts: Mapped[list["AccountModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,  # ← Использовать БД каскад
        single_parent=True,
    )
