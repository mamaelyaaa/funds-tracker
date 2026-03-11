from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.domain import CreatedAtDomainMixin
from domain.accounts.values import AccountId
from domain.goals.values import GoalId
from domain.users.values import UserId
from domain.values import Money, Percent
from .values import (
    FundId,
    FundDistributionId,
    FundRuleType,
    FundStatus,
)


@dataclass(kw_only=True)
class Fund(CreatedAtDomainMixin):
    """Доменная модель фиксированных остатков за период"""

    id: FundId = field(default_factory=FundId.generate)
    user_id: UserId
    total_amount: Money
    status: FundStatus = field(default=FundStatus.OPEN)
    start_date: datetime
    end_date: datetime

    @classmethod
    def create(
        cls,
        user_id: UserId,
        total_amount: Money,
        start_date: datetime,
        end_date: datetime,
        status: FundStatus = FundStatus.OPEN,
    ) -> "Fund":

        if start_date >= end_date:
            raise ...

        return cls(
            user_id=user_id,
            total_amount=total_amount,
            status=status,
            end_date=end_date,
            start_date=start_date,
        )

    def close(self) -> None:
        self.status = FundStatus.CLOSED
        self.end_date = datetime.now(timezone.utc)


@dataclass(kw_only=True)
class FundDistribution(CreatedAtDomainMixin):
    """Доменная модель остатка с историей"""

    id: FundDistributionId = field(default_factory=FundDistributionId.generate)
    fund_id: FundId
    reserve_id: AccountId | GoalId
    reserve_type: FundRuleType
    amount: Money
    percent_applied: Percent
