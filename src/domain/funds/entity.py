from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.mixins import DomainEventMixin, CreatedAtDomainMixin
from domain.accounts.values import AccountId
from domain.goals.values import GoalId
from domain.users.values import UserId
from domain.values import Money, Percentage
from .exceptions import InvalidFundDateException
from .values import (
    FundId,
    FundDistributionId,
    FundReserveType,
    FundStatus,
)


@dataclass(kw_only=True)
class Fund(CreatedAtDomainMixin, DomainEventMixin):
    """Доменная модель фиксированных остатков за период"""

    id: FundId = field(default_factory=FundId)
    user_id: UserId
    total_amount: Money
    status: FundStatus = field(default=FundStatus.OPEN)
    start_date: datetime
    end_date: datetime

    def __post_init__(self):
        if self.start_date > self.end_date:
            raise InvalidFundDateException

    def close(self) -> None:
        self.status = FundStatus.CLOSED
        self.end_date = datetime.now(timezone.utc)


@dataclass(kw_only=True)
class FundDistribution(CreatedAtDomainMixin):
    """Доменная модель остатка с историей"""

    id: FundDistributionId = field(default_factory=FundDistributionId)
    fund_id: FundId
    reserve_id: AccountId | GoalId
    reserve_type: FundReserveType
    amount: Money
    percent_applied: Percentage
