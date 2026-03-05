from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

from core.domain import DomainEvent


@dataclass(kw_only=True, frozen=True)
class BalanceUpdatedEvent(DomainEvent):
    """Баланс счета обновлен"""

    user_id: str
    account_id: str
    new_balance: Decimal
    delta: Decimal
    is_monthly_closing: bool


@dataclass(kw_only=True, frozen=True)
class AccountCreatedEvent(DomainEvent):
    user_id: str
    account_id: str
    new_balance: Decimal


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
