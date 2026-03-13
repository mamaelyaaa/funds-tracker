from dataclasses import dataclass
from datetime import datetime

from domain.funds.values import FundRuleType


@dataclass(frozen=True)
class CreateAllocationCommand:
    """Команда сохраняющая распределение"""

    user_id: str
    reserve_id: str
    reserve_type: FundRuleType
    percent: int


@dataclass(frozen=True)
class AllocateFundCommand:
    user_id: str
    total_amount: float
    end_date: datetime
    start_date: datetime


@dataclass(frozen=True)
class CreateFundCommand:
    user_id: str
    start_date: datetime
    end_date: datetime


@dataclass(frozen=True)
class UpdateFundCommand:
    user_id: str
    new_amount: float
    end_date: datetime


@dataclass(frozen=True)
class ReserveCreateCommand:
    reserve_id: str
    reserve_type: FundRuleType
    percent: int
