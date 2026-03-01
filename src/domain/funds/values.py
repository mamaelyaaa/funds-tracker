from dataclasses import dataclass
from enum import Enum

from core.domain import DomainIdValueObject, DomainValueObject
from domain.funds.exceptions import InvalidPercentException


@dataclass(frozen=True)
class FundId(DomainIdValueObject):
    pass


class FundRuleType(str, Enum):
    GOAL = "Goal"
    ACCOUNT = "Account"


@dataclass(frozen=True)
class FundRulesId(DomainIdValueObject):
    pass


@dataclass(frozen=True)
class FundDistributionId(DomainIdValueObject):
    pass


@dataclass(frozen=True)
class Percent(DomainValueObject[int]):

    def __post_init__(self):
        if not 0 <= self._value <= 100:
            raise InvalidPercentException


class FundStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    DISTRIBUTED = "Distributed"
