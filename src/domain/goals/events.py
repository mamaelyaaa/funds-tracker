from dataclasses import dataclass
from typing import Optional

from core.domain import DomainEvent
from domain.accounts.values import AccountId
from domain.goals.values import GoalId


@dataclass(kw_only=True, frozen=True)
class GoalAlreadyReachedEvent(DomainEvent):
    """Цель уже достигнута"""

    goal_id: GoalId
    account_id: Optional[AccountId]


@dataclass(kw_only=True, frozen=True)
class GoalLinkedToAccountEvent(DomainEvent):
    """Цель уже достигнута"""

    goal_id: str
    user_id: str
    account_id: str
