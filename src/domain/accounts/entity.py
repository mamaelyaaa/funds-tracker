from dataclasses import dataclass, field
from decimal import Decimal

from core.domain import TimestampDomainMixin, EventDomainMixin
from domain.users.values import UserId
from domain.values import Title, Money
from .events import BalanceUpdatedEvent, AccountCreatedEvent
from .values import AccountType, AccountCurrency, AccountId


@dataclass(kw_only=True)
class Account(TimestampDomainMixin, EventDomainMixin):
    """Доменная модель счета"""

    id: AccountId = field(default_factory=AccountId.generate)
    user_id: UserId
    name: Title
    balance: Money = field(default_factory=Money.zero)
    type: AccountType
    currency: AccountCurrency

    @classmethod
    def create(
        cls,
        user_id: UserId,
        name: Title,
        balance: Money,
        account_type: AccountType,
        currency: AccountCurrency,
    ) -> "Account":

        account: Account = cls(
            user_id=user_id,
            name=name,
            type=account_type,
            balance=balance,
            currency=currency,
        )
        account.events.append(
            AccountCreatedEvent(
                user_id=account.user_id.as_generic_type(),
                account_id=account.id.as_generic_type(),
                new_balance=balance.as_generic_type(),
            )
        )
        return account

    def update_balance(self, new_balance: Money, is_monthly_closing: bool) -> None:
        """Обновление баланса счета"""

        if self.balance == new_balance:
            return

        delta: Decimal = new_balance.as_generic_type() - self.balance.as_generic_type()
        self.balance = new_balance

        self._events.append(
            BalanceUpdatedEvent(
                user_id=self.user_id.as_generic_type(),
                account_id=self.id.as_generic_type(),
                new_balance=self.balance.as_generic_type(),
                delta=delta,
                is_monthly_closing=is_monthly_closing,
            )
        )
        self._touch()
