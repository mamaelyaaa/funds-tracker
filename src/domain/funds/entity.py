from dataclasses import dataclass, field
from datetime import datetime

from core.domain import CreatedAtDomainMixin
from domain.accounts.values import AccountId
from domain.goals.values import GoalId
from domain.users.values import UserId
from domain.values import Money
from .values import (
    FundId,
    FundDistributionId,
    FundRuleType,
    Percent,
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

    def update_status(self, new_status: FundStatus) -> None:
        if new_status == self.status:
            return


# @dataclass(kw_only=True)
# class FundRule(DomainEntity):
#     """Доменная модель правил распределения остатка по процентам"""
#
#     id: FundRulesId = field(default_factory=FundRulesId.generate)
#     user_id: UserId
#     reserve_id: AccountId | GoalId
#     reserve_type: FundRuleType
#     percent: Percent
#     updated_at: datetime = field(default_factory=datetime.now)
#
#     @classmethod
#     def create(
#         cls,
#         user_id: str,
#         reserve_id: str,
#         reserve_type: FundRuleType,
#         percent: int,
#     ) -> "FundRule":
#         return cls(
#             user_id=UserId(user_id),
#             reserve_type=reserve_type,
#             reserve_id=(
#                 AccountId(reserve_id)
#                 if reserve_type == FundRuleType.ACCOUNT
#                 else GoalId(reserve_id)
#             ),
#             percent=Percent(percent),
#         )


@dataclass(kw_only=True)
class FundDistribution(CreatedAtDomainMixin):
    """Доменная модель остатка с историей"""

    id: FundDistributionId = field(default_factory=FundDistributionId.generate)
    fund_id: FundId
    reserve_id: AccountId | GoalId
    reserve_type: FundRuleType
    amount: Money
    percent_applied: Percent
