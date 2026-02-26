from dataclasses import dataclass, field

from core.domain import DomainEntity
from domain.accounts.values import AccountId, Money
from .values import HistoryId


@dataclass(kw_only=True)
class History(DomainEntity):
    """Доменная модель истории счёта"""

    id: HistoryId = field(default_factory=HistoryId.generate)
    account_id: AccountId
    balance: Money
    delta: float
    is_monthly_closing: bool

    @classmethod
    def create(
        cls,
        account_id: str,
        balance: float,
        delta: float,
        is_monthly_closing: bool,
    ) -> "History":
        return cls(
            account_id=AccountId(account_id),
            balance=Money(balance),
            delta=delta,
            is_monthly_closing=is_monthly_closing,
        )
