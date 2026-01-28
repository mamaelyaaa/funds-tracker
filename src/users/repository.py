from typing import Protocol, Optional

from users.domain import User
from users.values import UserId


class UserRepositoryProtocol(Protocol):

    async def save(self, user: User) -> UserId:
        pass

    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        pass
