import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from core.events import DomainEvent


class AccountType(str, Enum):
    """Тип счета"""

    CARD = "Card"
    INVESTMENT = "Investment"
    CASH = "Cash"


@dataclass(frozen=True)
class AccountId:
    value: str

    @classmethod
    def generate(cls) -> "AccountId":
        return cls(value=str(uuid.uuid4()))

    @property
    def short(self) -> str:
        return self.value[:8]


@dataclass(frozen=True)
class BalanceUpdatedEvent(DomainEvent):
    """Баланс счета обновлен"""

    account_id: AccountId
    old_balance: float
    new_balance: float
    delta: float


@dataclass
class Account:
    """Доменная модель счета"""

    name: str
    type: AccountType
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
                account_id=self.id,
                new_balance=self.balance,
                old_balance=old_balance,
                delta=self.balance - old_balance,
                occurred_at=datetime.now(),
            )
        )

    @classmethod
    def create(cls, name: str, balance: float, account_type: AccountType) -> "Account":
        if balance < 0:
            raise ...
        return cls(name=name, type=account_type, balance=balance)

    @property
    def events(self) -> list[DomainEvent]:
        return self._events
