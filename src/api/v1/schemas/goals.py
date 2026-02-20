from datetime import datetime
from typing import Optional

from api.schemas import BaseApiModel


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
    created_at: datetime
