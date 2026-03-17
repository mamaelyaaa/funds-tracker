from dataclasses import dataclass
from datetime import datetime

from domain.commands import PaginationCommand
from domain.funds.values import FundReserveType


@dataclass(frozen=True)
class CheckReserveCommand:
    """Команда проверяющая распределение"""

    user_id: str
    reserve_id: str
    reserve_type: FundReserveType


@dataclass(frozen=True)
class CreateOrUpdateFundCommand:
    user_id: str
    account_id: str
    end_date: datetime


@dataclass(frozen=True)
class CreateReserveCommand:
    reserve_id: str
    reserve_type: FundReserveType
    percent: int


@dataclass(frozen=True)
class CreateReservesCommand:
    user_id: str
    reserves: list[CreateReserveCommand]


@dataclass(frozen=True)
class GetFundsCommand:
    user_id: str
    pagination: PaginationCommand


@dataclass(frozen=True)
class GetFundCommand:
    user_id: str
    fund_id: str
