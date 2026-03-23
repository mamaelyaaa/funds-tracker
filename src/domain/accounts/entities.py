from dataclasses import dataclass, field
from enum import Enum

from core.domain import DomainId
from core.mixins import DomainEventMixin, TimestampDomainMixin
from domain.users.values import UserId
from domain.values import Title, Money
from .events import (
    AccountCreatedEvent,
    BalanceUpdatedEvent,
)


class AccountId(DomainId):
    """Уникальный ID счета"""

    pass


class AccountType(str, Enum):
    """Тип счёта"""

    CARD = "Card"
    INVESTMENT = "Investment"
    CASH = "Cash"


class AccountCurrency(str, Enum):
    """Валюта счёта"""

    RUB = "RUB"
    USD = "USD"


@dataclass(kw_only=True)
class Account(DomainEventMixin, TimestampDomainMixin):
    """Доменная модель счета"""

    id: AccountId = field(default_factory=AccountId)
    user_id: UserId
    name: Title
    balance: Money = field(default_factory=Money)
    type: AccountType
    currency: AccountCurrency

    def __post_init__(self):
        self.events.append(
            AccountCreatedEvent(
                user_id=self.user_id,
                account_id=self.id,
                new_balance=self.balance,
            ),
        )

    def update_balance(self, new_balance: Money, is_monthly_closing: bool) -> None:
        """Обновление баланса счета"""

        self.balance = new_balance

        self.events.append(
            BalanceUpdatedEvent(
                user_id=self.user_id,
                account_id=self.id,
                new_balance=self.balance,
                delta=new_balance - self.balance,
                is_monthly_closing=is_monthly_closing,
            ),
        )
        self.touch()
