from dataclasses import dataclass
from enum import Enum

from core.domain import DomainIdValueObject


@dataclass(frozen=True)
class HistoryId(DomainIdValueObject):
    pass


class HistoryInterval(str, Enum):
    """Интервал с последней записи"""

    DAY = "1Day"
    WEEK1 = "1Week"
    MONTH1 = "1Month"
    MONTH6 = "6Months"
    YEAR = "1Year"
    ALL_TIME = "All"


class HistoryPeriod(str, Enum):
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
