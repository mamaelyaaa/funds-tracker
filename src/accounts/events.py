from dataclasses import dataclass

from accounts.values import AccountId, AccountCurrency
from core.domain import DomainEvent
from users.values import UserId


@dataclass(frozen=True)
class BalanceUpdatedEvent(DomainEvent):
    """Баланс счета обновлен"""

    user_id: UserId
    account_id: AccountId
    old_balance: float
    new_balance: float
    delta: float
    currency: AccountCurrency
