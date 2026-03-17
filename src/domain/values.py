import string
from dataclasses import dataclass
from decimal import Decimal

from core.domain import DomainValueObject
from domain.exceptions import (
    TooLargeTitleException,
    InvalidLettersTitleException,
    InvalidBalanceException,
)
from domain.funds.exceptions import InvalidPercentException

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


@dataclass(frozen=True)
class Money(DomainValueObject[Decimal]):
    ROUND_DIGITS = 2

    def __sub__(self, other: "Money") -> "Money":
        """Операция вычитания"""

        return Money(
            _value=(self._value - other._value).quantize(
                exp=Decimal("1." + self.ROUND_DIGITS * "0")
            )
        )

    def __post_init__(self):
        value = Decimal(str(self._value))
        value = value.quantize(exp=Decimal("1." + self.ROUND_DIGITS * "0"))
        object.__setattr__(self, "_value", value)

        if self._value < 0:
            raise InvalidBalanceException

    @classmethod
    def zero(cls) -> "Money":
        return cls(_value=Decimal("0"))

    def to_float(self) -> float:
        return float(self.as_generic_type())


@dataclass(frozen=True)
class Percent(DomainValueObject[Decimal]):

    def __post_init__(self):
        if not 0 <= self._value <= 100:
            raise InvalidPercentException
