from typing import Protocol, Optional

from .entity import User


class UserRepositoryProtocol(Protocol):

    async def save(self, user: User) -> str:
        pass

    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass
