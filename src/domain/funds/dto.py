from typing import Any

from domain.dto import BaseDTO
from domain.funds.entity import Fund
from domain.funds.values import FundId
from domain.users.values import UserId
from domain.values import Money


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
        }
        for excluded in excludes:
            data.pop(excluded)

        return data
