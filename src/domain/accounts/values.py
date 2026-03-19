from enum import Enum

from core.domain import DomainId


class AccountId(DomainId): ...


class AccountType(str, Enum):
    """Тип счёта"""

    CARD = "Card"
    INVESTMENT = "Investment"
    CASH = "Cash"


class AccountCurrency(str, Enum):
    """Валюта счёта"""

    RUB = "RUB"
    USD = "USD"
