from dataclasses import dataclass, field

from core.domain import DomainEntity, DomainEvent
from domain.users.values import UserId
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

    _events: list[DomainEvent] = field(default_factory=list)

    @property
    def events(self) -> list[DomainEvent]:
        return self._events

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
            )
        )

    def rename_account(self, new_name: Title) -> None:
        """Обновление названия счёта"""
        self.name = new_name
        return

    # def to_dict(self, all_str: bool = False) -> dict[str, Any]:
    #     return {
    #         "id": self.id.as_generic_type,
    #         "user_id": self.user_id.as_generic_type,
    #         "name": self.name.as_generic_type,
    #         "type": self.type,
    #         "balance": self.balance,
    #         "currency": self.currency,
    #         "created_at": (
    #             self.created_at if not all_str else self.created_at.isoformat()
    #         ),
    #     }
