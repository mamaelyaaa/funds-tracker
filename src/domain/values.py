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

    # def __post_init__(self):
    #     self.validate_length()
    #     self.validate_letters()
    #
    # def validate_length(self) -> None:
    #     if len(self.value) > self.MAX_LEN:
    #         raise TooLargeTitleException
    #
    # def validate_letters(self) -> None:


class Money(Decimal):

    def __new__(cls, value: Optional[Decimal | float | int] = None):
        val = Decimal(str(value)).quantize(Decimal("1.00")) or 0
        if val <= 0:
            raise InvalidBalanceException

        return super().__new__(cls, val)

    def __sub__(self, other: "Money") -> "Money":
        """Операция вычитания"""

        return Money(super().__sub__(other))

    # def __post_init__(self):
    # value = Decimal(str(self._value))
    # value = value.quantize(exp=Decimal("1." + self.ROUND_DIGITS * "0"))
    # object.__setattr__(self, "_value", value)

    # if self._value < 0:
    #     raise InvalidBalanceException

    # @classmethod
    # def zero(cls) -> "Money":
    #     return cls(value=Decimal("0"))
    #
    # def to_float(self) -> float:
    #     return float(self)


class Percentage(Decimal):

    def __new__(cls, value: Optional[Decimal | float] = None):
        val: Decimal = Decimal(str(value)).quantize(Decimal("1.00")) or 0

        if not 0 <= value <= 100:
            raise InvalidPercentException

        return super().__new__(cls, val)

    @classmethod
    def from_percent(cls, value: float):
        return cls(value / 100)

    # def __post_init__(self):
    #     if not 0 <= self.value <= 100:
    #         raise InvalidPercentException
