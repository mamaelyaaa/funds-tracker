from dataclasses import dataclass
from enum import Enum

from core.domain import DomainIdValueObject


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


class FundStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    DISTRIBUTED = "Distributed"
