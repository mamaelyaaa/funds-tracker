from enum import Enum

from core.domain import DomainId


class GoalId(DomainId): ...


class GoalStatus(str, Enum):
    """Статус цели"""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
