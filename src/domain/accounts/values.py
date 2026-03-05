from dataclasses import dataclass
from enum import Enum

from core.domain import DomainIdValueObject


class AccountType(str, Enum):
    """Тип счёта"""

    CARD = "Card"
    INVESTMENT = "Investment"
    CASH = "Cash"


class AccountCurrency(str, Enum):
    """Валюта счёта"""

    RUB = "RUB"
    USD = "USD"


@dataclass(frozen=True)
class AccountId(DomainIdValueObject):
    """Value-object уникального id счета"""

    pass
