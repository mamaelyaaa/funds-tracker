from dataclasses import dataclass
from datetime import datetime

from core.domain import DomainEvent
from domain.accounts.values import AccountCurrency


@dataclass(kw_only=True, frozen=True)
class BalanceUpdatedEvent(DomainEvent):
    """Баланс счета обновлен"""

    user_id: str
    account_id: str
    new_balance: float
    delta: float
    is_monthly_closing: bool


@dataclass(kw_only=True, frozen=True)
class AccountCreatedEvent(DomainEvent):
    user_id: str
    account_id: str
    new_balance: float


@dataclass(kw_only=True, frozen=True)
class FundCreatedEvent(DomainEvent):
    user_id: str
    end_date: datetime
    start_date: datetime


@dataclass(kw_only=True, frozen=True)
class FundUpdatedEvent(DomainEvent):
    user_id: str
    new_balance: float
    end_date: datetime
