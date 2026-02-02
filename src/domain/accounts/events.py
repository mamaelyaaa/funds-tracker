from dataclasses import dataclass

from domain.accounts.values import AccountId, AccountCurrency
from core.domain import DomainEvent
from domain.users.values import UserId


@dataclass(kw_only=True, frozen=True)
class BalanceUpdatedEvent(DomainEvent):
    """Баланс счета обновлен"""

    user_id: UserId
    account_id: AccountId
    old_balance: float
    new_balance: float
    delta: float
    currency: AccountCurrency


@dataclass(kw_only=True, frozen=True)
class AccountCreatedEvent(DomainEvent):
    user_id: UserId
    account_id: AccountId
    new_balance: float
