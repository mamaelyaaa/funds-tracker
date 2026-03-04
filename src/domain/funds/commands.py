from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.funds.values import FundRuleType


@dataclass(frozen=True)
class CreateAllocationCommand:
    """Команда сохраняющая распределение"""

    user_id: str
    reserve_id: str
    reserve_type: FundRuleType
    percent: int


@dataclass(frozen=True)
class FundDistributionCommand:
    reserve_id: str
    reserve_type: FundRuleType
    amount: float
    percent_applied: int


@dataclass(frozen=True)
class CreateFundCommand:
    user_id: str
    end_date: datetime
    start_date: Optional[datetime]


@dataclass(frozen=True)
class UpdateFundCommand:
    user_id: str
    new_amount: float
    end_date: datetime


@dataclass(frozen=True)
class CreateOrUpdateFundCommand:
    user_id: str
    new_amount: float
    end_date: datetime
    start_date: datetime
