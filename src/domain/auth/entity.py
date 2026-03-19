from dataclasses import dataclass, field
from datetime import datetime

from core.domain import DomainId
from core.mixins import TimestampDomainMixin
from domain.users.values import UserId


class UserSessionId(DomainId): ...


@dataclass(kw_only=True)
class UserSession(TimestampDomainMixin):
    """Доменная модель сессий пользователя"""

    id: UserSessionId = field(default_factory=UserSessionId)
    user_id: UserId
    refresh_jti: str
    expires_in: datetime
