from dataclasses import dataclass

from core.domain import DomainIdValueObject


@dataclass(frozen=True)
class UserId(DomainIdValueObject):
    """Value-obj уникального id пользователя"""

    @property
    def short(self) -> str:
        return self._value[:8]
