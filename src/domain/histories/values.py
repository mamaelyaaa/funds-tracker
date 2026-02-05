import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from core.domain import DomainValueObject


@dataclass(frozen=True)
class HistoryId(DomainValueObject[str]):

    @classmethod
    def generate(cls) -> "HistoryId":
        return cls(value=str(uuid.uuid4()))


class HistoryInterval(str, Enum):
    """Интервал с последней записи"""

    MONTH1 = "1Month"
    MONTH6 = "6Months"
    YEAR = "1Year"
    ALL_TIME = "All"


class HistoryPeriod(str, Enum):
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
