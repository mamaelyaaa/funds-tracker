from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.models import AccountModel
from infra.models import Base
from infra.models.mixin import DataMixin


class SavingsHistoryModel(Base, DataMixin):
    __tablename__ = "savings_history"

    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.id", name="fk_savings_acc_id", ondelete="CASCADE")
    )
    balance: Mapped[float] = mapped_column(default=0.0)

    account: Mapped["AccountModel"] = relationship(backref="savings")
