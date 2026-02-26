from sqlalchemy import ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .accounts import AccountModel
from .base import Base
from .mixin import DateMixin


class HistoryModel(Base, DateMixin):
    __tablename__ = "accounts_history"
    __table_args__ = (CheckConstraint("balance >= 0", name="history_balance_gt_0"),)

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.id", name="fk_savings_acc_id", ondelete="CASCADE")
    )
    balance: Mapped[float]
    delta: Mapped[float]
    is_monthly_closing: Mapped[bool] = mapped_column(default=False)

    account: Mapped["AccountModel"] = relationship(backref="histories")
