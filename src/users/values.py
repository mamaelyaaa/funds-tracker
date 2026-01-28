import uuid
from dataclasses import dataclass

from core.domain import DomainValueObject


@dataclass(frozen=True)
class UserId(DomainValueObject[str]):
    """Value-obj уникального id пользователя"""

    @classmethod
    def generate(cls) -> "UserId":
        return cls(value=str(uuid.uuid4()))

    @property
    def short(self) -> str:
        return self.value[:8]
