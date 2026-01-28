from dataclasses import dataclass, field
from datetime import datetime

from core.domain import DomainEvent
from users.values import UserId
from .values import AccountType, AccountCurrency, AccountId


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
    name: str
    type: AccountType
    currency: AccountCurrency
    balance: float = field(default=0)

    id: AccountId = field(default_factory=AccountId.generate)
    created_at: datetime = field(default_factory=datetime.now)

    _events: list[DomainEvent] = field(default_factory=list)

    def update_balance(self, new_balance: float) -> None:
        """Обновление баланса счета"""

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

    def rename_account(self, new_name: str) -> None:
        """Обновление названия счёта"""
        if len(new_name) > 63:
            # TODO Сделать ошибку на TooLarge
            raise ...
        self.name = new_name
        return

    @classmethod
    def create(
        cls,
        user_id: UserId,
        name: str,
        balance: float,
        account_type: AccountType,
        currency: AccountCurrency,
    ) -> "Account":
        if balance < 0:
            # TODO сделать ошибку
            raise ...
        return cls(
            user_id=user_id,
            name=name,
            type=account_type,
            balance=balance,
            currency=currency,
        )

    @property
    def events(self) -> list[DomainEvent]:
        return self._events
