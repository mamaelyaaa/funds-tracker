import uuid
from dataclasses import dataclass
from enum import Enum

from core.domain import DomainValueObject


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
class AccountId(DomainValueObject[str]):
    """Value-object уникального id счета"""

    @classmethod
    def generate(cls) -> "AccountId":
        return cls(value=str(uuid.uuid4()))

    @property
    def short(self) -> str:
        return self.value[:8]
