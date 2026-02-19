from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any

from core.domain import DomainEntity
from domain.users.values import UserId
from .commands import CreateAccountCommand
from .events import BalanceUpdatedEvent, AccountCreatedEvent
from .exceptions import InvalidInitBalanceException
from .values import AccountType, AccountCurrency, AccountId, Title


@dataclass(kw_only=True)
class Account(DomainEntity):
    """Доменная модель счета"""

    id: AccountId = field(default_factory=AccountId.generate)
    user_id: UserId
    name: Title
    type: AccountType
    currency: AccountCurrency
    balance: float = field(default=0.0)

    @classmethod
    def create(
        cls,
        user_id: str,
        name: str,
        balance: float,
        account_type: AccountType,
        currency: AccountCurrency,
    ) -> "Account":
        if balance < 0:
            raise InvalidInitBalanceException

        account = cls(
            user_id=UserId(user_id),
            name=Title(name),
            type=account_type,
            balance=balance,
            currency=currency,
        )
        account.events.append(
            AccountCreatedEvent(
                user_id=UserId(user_id),
                account_id=account.id,
                new_balance=balance,
            )
        )
        return account

    @classmethod
    def create_from_command(cls, command: CreateAccountCommand) -> "Account":
        if command.balance < 0:
            raise InvalidInitBalanceException
        return cls(**asdict(command))

    def update_balance(self, new_balance: float) -> None:
        """Обновление баланса счета"""

        if self.balance == new_balance:
            return

        if new_balance < 0:
            raise InvalidInitBalanceException

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

    def to_dict(self, all_str: bool = False) -> dict[str, Any]:
        return {
            "id": self.id.value,
            "user_id": self.user_id.value,
            "name": self.name.value,
            "type": self.type,
            "balance": self.balance,
            "currency": self.currency,
            "created_at": (
                self.created_at if not all_str else self.created_at.isoformat()
            ),
        }
