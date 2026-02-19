from datetime import datetime
from typing import Optional

from api.schemas import BaseApiModel
from domain.goals.entities import Goal


class CreateGoalSchema(BaseApiModel):
    title: str
    target_amount: float
    account_id: Optional[str] = None
    deadline: Optional[datetime] = None
    savings_percentage: float = 0.2


class UpdateGoalSchema(BaseApiModel):
    title: Optional[str] = None
    target_amount: Optional[float] = None
    account_id: Optional[str] = None
    unlink_account: Optional[bool] = None
    deadline: Optional[datetime] = None
    savings_percentage: Optional[float] = None


class GoalDetailSchema(BaseApiModel):
    id: str
    user_id: str
    account_id: Optional[str]
    title: str
    target_amount: float
    current_amount: float
    savings_percentage: float = 0.2
    deadline: Optional[datetime]

    @classmethod
    def from_entity(cls, goal: Goal) -> "GoalDetailSchema":
        return cls(
            id=goal.id.value,
            user_id=goal.user_id.value,
            title=goal.title.value,
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            savings_percentage=goal.savings_percentage.value,
            account_id=goal.account_id.value if goal.account_id else None,
            deadline=goal.deadline,
        )
