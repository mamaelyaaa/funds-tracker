from dataclasses import dataclass
from enum import Enum

from core.domain import DomainValueObject, DomainIdValueObject
from domain.goals.exceptions import InvalidGoalPercentageException


@dataclass(frozen=True)
class GoalId(DomainIdValueObject):
    pass


@dataclass(frozen=True)
class GoalPercentage(DomainValueObject[float]):

    def as_generic_type(self) -> float:
        return self._value

    def __post_init__(self):
        if not 0 < self.as_generic_type() <= 1:
            raise InvalidGoalPercentageException


class GoalStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
