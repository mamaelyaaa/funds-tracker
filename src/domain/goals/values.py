import uuid
from dataclasses import dataclass
from enum import Enum

from core.domain import DomainValueObject
from domain.goals.exceptions import InvalidGoalPercentageException


@dataclass(frozen=True)
class GoalId(DomainValueObject[str]):

    def as_generic_type(self) -> str:
        return self._value

    @classmethod
    def generate(cls) -> "GoalId":
        return cls(_value=str(uuid.uuid4()))


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
