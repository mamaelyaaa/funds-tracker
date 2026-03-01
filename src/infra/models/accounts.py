from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.accounts.values import AccountType, AccountCurrency, Title

if TYPE_CHECKING:
    from . import UserModel, HistoryModel

from .base import Base
from .mixin import TimeStampMixin


class AccountModel(Base, TimeStampMixin):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uc_user_id_with_name"),
        CheckConstraint("balance >= 0", name="account_balance_gt_0"),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", name="fk_acc_user_id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(Title.MAX_LEN), index=True)
    type: Mapped[AccountType]
    balance: Mapped[float]
    currency: Mapped[AccountCurrency]

    # Отношения
    user: Mapped["UserModel"] = relationship(
        back_populates="accounts",
    )
    histories: Mapped[list["HistoryModel"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
