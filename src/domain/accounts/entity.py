from dataclasses import dataclass, field
from datetime import datetime

from core.domain import DomainEntity, DomainEvent
from domain.users.values import UserId
from .events import BalanceUpdatedEvent, AccountCreatedEvent
from .values import AccountType, AccountCurrency, AccountId, Title, Money


@dataclass(kw_only=True)
class Account(DomainEntity):
    """Доменная модель счета"""

    id: AccountId = field(default_factory=AccountId.generate)
    user_id: UserId
    name: Title
    type: AccountType
    currency: AccountCurrency
    balance: Money = field(default_factory=Money.zero)
    updated_at: datetime = field(default_factory=datetime.now)

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

        account = cls(
            user_id=UserId(user_id),
            name=Title(name),
            type=account_type,
            balance=Money(balance),
            currency=currency,
        )
        account.events.append(
            AccountCreatedEvent(
                user_id=account.user_id.as_generic_type(),
                account_id=account.id.as_generic_type(),
                new_balance=balance,
                occurred_at=account.updated_at,
            )
        )
        return account

    def update_balance(
        self, new_balance: Money, is_monthly_closing: bool, occurred_at: datetime
    ) -> None:
        """Обновление баланса счета"""

        if self.balance == new_balance:
            return

        delta = float(
            f"{new_balance.as_generic_type() - self.balance.as_generic_type():.{Money.MAX_DIGITS}f}"
        )
        self.balance = new_balance

        self._events.append(
            BalanceUpdatedEvent(
                user_id=self.user_id.as_generic_type(),
                account_id=self.id.as_generic_type(),
                new_balance=new_balance.as_generic_type(),
                delta=delta,
                is_monthly_closing=is_monthly_closing,
                occurred_at=occurred_at,
            )
        )
        self.updated_at = datetime.now()

    # def rename_account(self, new_name: Title) -> None:
    #     """Обновление названия счёта"""
    #     self.name = new_name
    #     return
