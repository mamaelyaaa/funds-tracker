from enum import Enum

from core.domain import DomainId


class HistoryId(DomainId): ...


class HistoryInterval(str, Enum):
    """Интервал с последней записи"""

    DAY = "1Day"
    WEEK1 = "1Week"
    MONTH1 = "1Month"
    MONTH6 = "6Months"
    YEAR = "1Year"
    ALL_TIME = "All"


class HistoryPeriod(str, Enum):
    """Периоды для группировки дат"""

    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
