from dataclasses import dataclass

from core.domain import DomainEvent
from domain.accounts.values import AccountCurrency


@dataclass(kw_only=True, frozen=True)
class BalanceUpdatedEvent(DomainEvent):
    """Баланс счета обновлен"""

    user_id: str
    account_id: str
    new_balance: float
    delta: float
    is_monthly_closing: bool


@dataclass(kw_only=True, frozen=True)
class AccountCreatedEvent(DomainEvent):
    user_id: str
    account_id: str
    new_balance: float
