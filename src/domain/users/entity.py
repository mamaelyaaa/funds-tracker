from dataclasses import dataclass, field

from core.mixins import CreatedAtDomainMixin

from .values import UserId


@dataclass(kw_only=True)
class User(CreatedAtDomainMixin):
    """Доменная модель пользователя"""

    MAX_ACCOUNTS: int = 10

    id: UserId = field(default_factory=UserId)
    name: str
