from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from core.domain import DomainEvent
from users.values import UserId
from .exceptions import InvalidInitBalanceException
from .values import AccountType, AccountCurrency, AccountId, Title


@dataclass(frozen=True)
class BalanceUpdatedEvent(DomainEvent):
    """Баланс счета обновлен"""

    user_id: UserId
    account_id: AccountId
    old_balance: float
    new_balance: float
    delta: float
    currency: AccountCurrency


@dataclass
class Account:
    """Доменная модель счета"""

    user_id: UserId
    name: Title
    type: AccountType
    currency: AccountCurrency
    balance: float = field(default=0)

    id: AccountId = field(default_factory=AccountId.generate)
    created_at: datetime = field(default_factory=datetime.now)

    _events: list[DomainEvent] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        user_id: UserId,
        name: Title,
        balance: float,
        account_type: AccountType,
        currency: AccountCurrency,
    ) -> "Account":
        if balance < 0:
            raise InvalidInitBalanceException
        return cls(
            user_id=user_id,
            name=name,
            type=account_type,
            balance=balance,
            currency=currency,
        )

    def update_balance(self, new_balance: float) -> None:
        """Обновление баланса счета"""

        if self.balance == new_balance:
            return

        old_balance = self.balance
        self.balance = new_balance

        self._events.append(
            BalanceUpdatedEvent(
                user_id=self.user_id,
                account_id=self.id,
                new_balance=self.balance,
                old_balance=old_balance,
                delta=self.balance - old_balance,
                currency=self.currency,
                occurred_at=datetime.now(),
            )
        )

    def rename_account(self, new_name: Title) -> None:
        """Обновление названия счёта"""
        self.name = new_name
        return

    @property
    def events(self) -> list[DomainEvent]:
        return self._events

    def model_dump(self) -> dict[str, Any]:
        return {
            "id": self.id.value,
            "user_id": self.user_id.value,
            "name": self.name.value,
            "type": self.type,
            "balance": self.balance,
            "currency": self.currency,
            "created_at": self.created_at,
        }
