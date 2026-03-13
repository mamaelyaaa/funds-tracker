from dataclasses import dataclass

from core.domain import DomainIdValueObject


@dataclass(frozen=True)
class UserId(DomainIdValueObject):
    """Value-obj уникального id пользователя"""

    pass
