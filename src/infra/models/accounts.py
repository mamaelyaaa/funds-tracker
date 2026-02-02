from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.accounts.values import AccountType, AccountCurrency

if TYPE_CHECKING:
    from infra.models import UserModel

from .base import Base
from .mixin import DataMixin


class AccountModel(Base, DataMixin):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uc_user_id_with_name"),)

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", name="fk_acc_user_id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(index=True)
    type: Mapped[AccountType]
    balance: Mapped[float] = mapped_column(default=0.0)
    currency: Mapped[AccountCurrency]

    user: Mapped["UserModel"] = relationship(
        back_populates="accounts",
    )
