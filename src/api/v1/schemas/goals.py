from datetime import datetime
from typing import Optional

from pydantic import Field

from api.schemas import BaseApiModel


class CreateGoalSchema(BaseApiModel):
    title: str
    target_amount: float
    current_amount: float
    deadline: Optional[datetime] = Field(default=None)


class UpdateGoalSchema(BaseApiModel):
    title: Optional[str] = None
    target_amount: Optional[float] = None
    deadline: Optional[datetime] = None


class GoalDetailSchema(BaseApiModel):
    id: str
    user_id: str
    title: str
    target_amount: float
    current_amount: float
    deadline: Optional[datetime]
    created_at: datetime
