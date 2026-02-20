from dataclasses import dataclass
from typing import Optional

from core.domain import DomainEvent


@dataclass(kw_only=True, frozen=True)
class GoalAlreadyReachedEvent(DomainEvent):
    """Цель уже достигнута"""

    goal_id: str
    account_id: Optional[str]


@dataclass(kw_only=True, frozen=True)
class GoalLinkedToAccountEvent(DomainEvent):
    """Цель уже достигнута"""

    goal_id: str
    user_id: str
    account_id: str
