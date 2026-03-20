from dataclasses import dataclass, field
from datetime import datetime

from core.domain import DomainId
from core.mixins import TimestampDomainMixin
from domain.users.values import UserId


class UserSessionId(DomainId): ...


@dataclass(kw_only=True)
class UserSession(TimestampDomainMixin):
    """Доменная модель сессий пользователя"""

    MAX_AUTHORIZED: int = 5

    id: UserSessionId = field(default_factory=UserSessionId)
    user_id: UserId
    refresh_jti: str
    fingerprint: str
    expires_in: datetime

    def __post_init__(self):
        if self.created_at > self.expires_in:
            print(self.created_at)
            print(self.expires_in)
            raise ValueError("Чето не то")
