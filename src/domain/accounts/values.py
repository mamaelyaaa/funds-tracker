import string
from dataclasses import dataclass
from enum import Enum

from core.domain import DomainValueObject, DomainIdValueObject
from domain.accounts.exceptions import (
    TooLargeTitleException,
    InvalidLettersTitleException,
)


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
        if len(self._value) > self.MAX_LEN:
            raise TooLargeTitleException

    def validate_letters(self) -> None:
        for char in self._value:
            if char not in alphabet:
                raise InvalidLettersTitleException
