from dataclasses import dataclass
from enum import Enum

from core.domain import DomainId


class FundId(DomainId): ...


class FundDistributionId(DomainId): ...


class FundReserveType(str, Enum):
    """Тип резерва под остаток"""

    GOAL = "Goal"
    ACCOUNT = "Account"


class FundStatus(str, Enum):
    """Статус накопленного остатка"""

    OPEN = "Open"
    CLOSED = "Closed"
    DISTRIBUTED = "Distributed"
