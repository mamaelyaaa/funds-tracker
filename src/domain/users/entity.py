from dataclasses import dataclass, field

from core.domain import CreatedAtDomainMixin
from .values import UserId


@dataclass(kw_only=True)
class User(CreatedAtDomainMixin):
    """Доменная модель пользователя"""

    MAX_ACCOUNTS: int = 10

    id: UserId = field(default_factory=UserId.generate)
    name: str
