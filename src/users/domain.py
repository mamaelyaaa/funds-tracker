from dataclasses import dataclass, field
from datetime import datetime

from users.values import UserId


@dataclass
class User:
    """Доменная модель пользователя"""

    name: str

    MAX_ACCOUNTS: int = 10

    id: UserId = field(default_factory=UserId.generate)
    created_at: datetime = field(default_factory=datetime.now)
