from dataclasses import dataclass, field

from core.mixins import DomainEventMixin, TimestampDomainMixin
from .values import UserId, Username


@dataclass(kw_only=True)
class User(DomainEventMixin, TimestampDomainMixin):
    """Доменная модель пользователя"""

    MAX_ACCOUNTS: int = 10

    id: UserId = field(default_factory=UserId)
    username: Username
    password: str

    # def change_username(self, new_username: Username) -> None:
    #     self.username = new_username
    #     self.events.append(...)
