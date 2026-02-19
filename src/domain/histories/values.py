from dataclasses import dataclass
from enum import Enum

from core.domain import DomainIdValueObject


@dataclass(frozen=True)
class HistoryId(DomainIdValueObject):
    pass


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
