import uuid
from dataclasses import dataclass
from enum import Enum

from core.domain import DomainValueObject
from domain.goals.exceptions import InvalidGoalPercentageException


@dataclass(frozen=True)
class GoalId(DomainValueObject[str]):

    @classmethod
    def generate(cls) -> "GoalId":
        return cls(value=str(uuid.uuid4()))


@dataclass(frozen=True)
class GoalPercentage(DomainValueObject[float]):

    def __post_init__(self):
        if not 0 < self.value <= 1:
            raise InvalidGoalPercentageException


class GoalStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
