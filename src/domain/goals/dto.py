from typing import Any

from domain.accounts.values import Title, AccountId
from domain.dto import BaseDTO
from domain.users.values import UserId
from .entities import Goal
from .values import GoalPercentage, GoalId


class GoalDTO(BaseDTO):

    @staticmethod
    def from_entity_to_dict(model: Goal, excludes: list[str] = None) -> dict[str, Any]:
        if not excludes:
            excludes = []

        data = {
            "id": model.id.as_generic_type(),
            "user_id": model.user_id.as_generic_type(),
            "account_id": (
                model.account_id.as_generic_type() if model.account_id else None
            ),
            "title": model.title.as_generic_type(),
            "savings_percentage": model.savings_percentage.as_generic_type(),
            "status": model.status,
            "target_amount": model.target_amount,
            "deadline": model.deadline if model.deadline else None,
            "current_amount": model.current_amount,
            "created_at": model.created_at,
        }
        for excluded in excludes:
            data.pop(excluded)

        return data

    @staticmethod
    def from_dict_to_entity(data: dict[str, Any]) -> Goal:
        return Goal(
            id=GoalId(data.get("id")),
            user_id=UserId(data.get("user_id")),
            account_id=(
                AccountId(data.get("account_id")) if data.get("account_id") else None
            ),
            title=Title(data.get("title")),
            target_amount=data.get("target_amount"),
            current_amount=data.get("current_amount"),
            status=data.get("status"),
            savings_percentage=GoalPercentage(data.get("savings_percentage")),
            deadline=data.get("deadline") if data.get("deadline") else None,
            created_at=data.get("created_at"),
        )
