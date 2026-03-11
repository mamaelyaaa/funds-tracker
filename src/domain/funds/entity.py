from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.domain import CreatedAtDomainMixin, EventDomainMixin
from domain.accounts.values import AccountId
from domain.goals.values import GoalId
from domain.users.values import UserId
from domain.values import Money, Percent
from .events import FundClosedEvent
from .exceptions import InvalidFundDateException
from .values import (
    FundId,
    FundDistributionId,
    FundRuleType,
    FundStatus,
)


@dataclass(init=False, kw_only=True)
class Fund(CreatedAtDomainMixin, EventDomainMixin):
    """Доменная модель фиксированных остатков за период"""

    # id: FundId = field(default_factory=FundId.generate)
    # user_id: UserId
    # total_amount: Money
    # status: FundStatus = field(default=FundStatus.OPEN)
    # start_date: datetime
    # end_date: datetime

    def __init__(
        self,
        user_id: UserId,
        total_amount: Money,
        start_date: datetime,
        end_date: datetime,
        id: FundId = FundId.generate(),
        status: FundStatus = FundStatus.OPEN,
        created_at: datetime = datetime.now(timezone.utc),
    ):
        self.id = id
        self.user_id = user_id
        self.total_amount = total_amount
        self.status = status
        self.start_date, self.end_date = self._validate_dates(start_date, end_date)
        self.created_at = created_at

    @staticmethod
    def _validate_dates(start_date, end_date) -> tuple[datetime, datetime]:
        if start_date > end_date:
            raise InvalidFundDateException
        return start_date, end_date

    def close(self) -> None:
        self.status = FundStatus.CLOSED
        self.end_date = datetime.now(timezone.utc)
        self._events.append(
            FundClosedEvent(
                user_id=self.user_id.as_generic_type(),
                fund_id=self.id.as_generic_type(),
            )
        )


@dataclass(kw_only=True)
class FundDistribution(CreatedAtDomainMixin):
    """Доменная модель остатка с историей"""

    id: FundDistributionId = field(default_factory=FundDistributionId.generate)
    fund_id: FundId
    reserve_id: AccountId | GoalId
    reserve_type: FundRuleType
    amount: Money
    percent_applied: Percent
