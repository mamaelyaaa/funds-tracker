from dataclasses import dataclass
from enum import Enum

from core.domain import DomainIdValueObject


@dataclass(frozen=True)
class FundId(DomainIdValueObject):
    pass


class FundReserveType(str, Enum):
    """Тип резерва под остаток"""

    GOAL = "Goal"
    ACCOUNT = "Account"


@dataclass(frozen=True)
class FundDistributionId(DomainIdValueObject):
    pass


class FundStatus(str, Enum):
    """Статус накопленного остатка"""

    OPEN = "Open"
    CLOSED = "Closed"
    DISTRIBUTED = "Distributed"
