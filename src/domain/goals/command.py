from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.accounts.entity import Account
from domain.goals.values import GoalPercentage


@dataclass(frozen=True)
class CreateGoalCommand:
    """Команда на создание цели"""

    title: str
    target_amount: float
    user_id: str
    account: Optional[Account] = None
    deadline: Optional[datetime] = None
    savings_percentage: float = 0.2


@dataclass(frozen=True)
class GetUserGoalsCommand:
    """Команда на получение целей пользователя"""

    user_id: str
    account_id: Optional[str] = None
    deadline: Optional[datetime] = None
    savings_percentage: Optional[GoalPercentage] = None


@dataclass(frozen=True)
class UpdateGoalPartiallyCommand:
    """Команда на обновление цели (для patch)"""

    goal_id: str
    user_id: str
    title: Optional[str] = None
    current_amount: Optional[float] = None
    target_amount: Optional[float] = None
    account: Optional[Account] = None
    deadline: Optional[datetime] = None
    savings_percentage: Optional[float] = None
    unlink_account: Optional[bool] = None
