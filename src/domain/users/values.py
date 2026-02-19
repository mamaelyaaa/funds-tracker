import uuid
from dataclasses import dataclass

from core.domain import DomainValueObject


@dataclass(frozen=True)
class UserId(DomainValueObject[str]):
    """Value-obj уникального id пользователя"""

    def as_generic_type(self) -> str:
        return str(self._value)

    @classmethod
    def generate(cls) -> "UserId":
        return cls(_value=str(uuid.uuid4()))

    @property
    def short(self) -> str:
        return self._value[:8]
