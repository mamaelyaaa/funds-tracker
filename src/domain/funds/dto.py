from typing import Any

from domain.accounts.values import AccountId
from domain.dto import BaseDTO
from domain.funds.entity import Fund, FundDistribution
from domain.funds.values import FundId, FundDistributionId, FundReserveType
from domain.goals.values import GoalId
from domain.users.values import UserId
from domain.values import Money, Percent


class FundDTO(BaseDTO):

    @staticmethod
    def from_dict_to_entity(data: dict[str, Any]) -> Fund:
        return Fund(
            id=FundId(data.get("id")),
            user_id=UserId(data.get("user_id")),
            total_amount=Money(data.get("total_amount")),
            status=data.get("status"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            created_at=data.get("created_at"),
        )

    @staticmethod
    def from_entity_to_dict(model: Fund, excludes: list[str] = None) -> dict[str, Any]:
        if not excludes:
            excludes = []

        data = {
            "id": model.id.as_generic_type(),
            "user_id": model.user_id.as_generic_type(),
            "total_amount": model.total_amount.as_generic_type(),
            "status": model.status,
            "start_date": model.start_date,
            "end_date": model.end_date,
            "created_at": model.created_at,
        }
        for excluded in excludes:
            data.pop(excluded)

        return data


class FundDistDTO(BaseDTO):

    @staticmethod
    def from_dict_to_entity(data: dict[str, Any]) -> FundDistribution:
        return FundDistribution(
            id=FundDistributionId(data.get("id")),
            fund_id=FundId(data.get("fund_id")),
            reserve_id=(
                AccountId(data.get("reserve_id"))
                if data.get("status") == FundReserveType.ACCOUNT
                else GoalId(data.get("reserve_id"))
            ),
            reserve_type=data.get("reserve_type"),
            amount=Money(data.get("amount")),
            percent_applied=Percent(data.get("percent_applied")),
            created_at=data.get("created_at"),
        )

    @staticmethod
    def from_entity_to_dict(
        model: FundDistribution, excludes: list[str] = None
    ) -> dict[str, Any]:
        if not excludes:
            excludes = []

        data = {
            "id": model.id.as_generic_type(),
            "fund_id": model.fund_id.as_generic_type(),
            "reserve_id": model.reserve_id.as_generic_type(),
            "reserve_type": model.reserve_type,
            "amount": model.amount.as_generic_type(),
            "percent_applied": model.percent_applied.as_generic_type(),
            "created_at": model.created_at,
        }
        for excluded in excludes:
            data.pop(excluded)

        return data
