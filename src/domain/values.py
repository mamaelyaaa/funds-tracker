import string
from decimal import Decimal
from typing import Optional

from domain.exceptions import (
    TooLargeTitleException,
    InvalidLettersTitleException,
    InvalidBalanceException,
    InvalidPercentException,
)

alphabet = (
    string.ascii_letters
    + string.digits
    + "".join(chr(i) for i in range(ord("а"), ord("я") + 1))
    + "".join(chr(i) for i in range(ord("А"), ord("Я") + 1))
    + " "
    + "ё"
)


class Title(str):
    """Value-object заголовка счёта (названия)"""

    MAX_LEN: int = 63

    def __new__(cls, value: str):
        if len(value) > cls.MAX_LEN:
            raise TooLargeTitleException

        for char in value:
            if char not in alphabet:
                raise InvalidLettersTitleException

        return super().__new__(cls, value)


class Money(Decimal):

    def __new__(cls, value: Optional[Decimal | float | int] = None):
        val = Decimal(str(value)).quantize(Decimal("1.00")) or Decimal("0")
        if val < 0:
            raise InvalidBalanceException

        return super().__new__(cls, val)

    def __sub__(self, other: "Money") -> "Money":
        """Операция вычитания"""

        return Money(super().__sub__(other))


class Percentage(Decimal):

    def __new__(cls, value: Optional[Decimal | float] = None):
        val: Decimal = Decimal(str(value)).quantize(Decimal("1.00")) or 0

        if not 0 <= value <= 100:
            raise InvalidPercentException

        return super().__new__(cls, val)

    @classmethod
    def from_percent(cls, value: float):
        return cls(value / 100)
