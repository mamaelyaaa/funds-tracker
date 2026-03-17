from dataclasses import dataclass
from enum import Enum

from core.domain import DomainIdValueObject


@dataclass(frozen=True)
class GoalId(DomainIdValueObject):
    pass


class GoalStatus(str, Enum):
    """Статус цели"""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
