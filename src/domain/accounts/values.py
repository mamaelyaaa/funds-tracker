import uuid
from dataclasses import dataclass
from enum import Enum
import string

from domain.accounts.exceptions import (
    TooLargeTitleException,
    InvalidLettersTitleException,
)
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


alphabet = (
    string.ascii_letters
    + string.digits
    + "".join(chr(i) for i in range(ord("а"), ord("я") + 1))
    + "".join(chr(i) for i in range(ord("А"), ord("Я") + 1))
    + " "
    + "ё"
)


@dataclass(frozen=True)
class Title(DomainValueObject[str]):
    """Value-object заголовка счёта (названия)"""

    MAX_LEN: int = 63

    def __post_init__(self):
        self.validate_length()
        self.validate_letters()

    def validate_length(self) -> None:
        if len(self.value) > self.MAX_LEN:
            raise TooLargeTitleException

    def validate_letters(self) -> None:
        for char in self.value:
            if char not in alphabet:
                raise InvalidLettersTitleException
