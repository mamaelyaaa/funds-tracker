from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.commands import PaginationCommand


@dataclass(frozen=True)
class CreateGoalCommand:
    """Команда на создание цели"""

    title: str
    user_id: str
    target_amount: float
    current_amount: float = 0
    deadline: Optional[datetime] = None


@dataclass(frozen=True)
class GetGoalCommand:
    """Команда на получение цели пользователя"""

    user_id: str
    goal_id: str


@dataclass(frozen=True)
class GetGoalsCommand:
    """Команда на получение целей пользователя"""

    user_id: str
    pagination: PaginationCommand


@dataclass(frozen=True)
class UpdateGoalPartiallyCommand:
    """Команда на обновление цели (для patch)"""

    goal_id: str
    user_id: str
    title: Optional[str] = None
    current_amount: Optional[float] = None
    target_amount: Optional[float] = None
    deadline: Optional[datetime] = None
