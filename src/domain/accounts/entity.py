from dataclasses import dataclass, field
from decimal import Decimal

from core.domain import TimestampDomainMixin, EventDomainMixin
from domain.users.values import UserId
from domain.values import Title, Money
from .events import (
    AccountCreatedEvent,
    BalanceUpdatedEvent,
)
from .values import AccountType, AccountCurrency, AccountId


@dataclass(kw_only=True)
class Account(EventDomainMixin, TimestampDomainMixin):
    """Доменная модель счета"""

    id: AccountId = field(default_factory=AccountId.generate)
    user_id: UserId
    name: Title
    balance: Money = field(default_factory=Money.zero)
    type: AccountType
    currency: AccountCurrency

    def __post_init__(self):
        self.events.append(
            AccountCreatedEvent(
                user_id=self.user_id.as_generic_type(),
                account_id=self.id.as_generic_type(),
                new_balance=self.balance.as_generic_type(),
            ),
        )

    def update_balance(self, new_balance: Money, is_monthly_closing: bool) -> None:
        """Обновление баланса счета"""

        delta: Decimal = new_balance.as_generic_type() - self.balance.as_generic_type()
        self.balance = new_balance

        self.events.append(
            BalanceUpdatedEvent(
                user_id=self.user_id.as_generic_type(),
                account_id=self.id.as_generic_type(),
                new_balance=self.balance.as_generic_type(),
                delta=delta,
                is_monthly_closing=is_monthly_closing,
            ),
        )
        self._touch()
