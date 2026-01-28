from functools import lru_cache
from typing import Optional, Annotated

from fastapi import Depends

from users.domain import User
from users.repository import UserRepositoryProtocol
from users.values import UserId


class InMemoryUserRepository:

    def __init__(self):
        self._storage: dict[UserId, User] = {}

    async def save(self, user: User) -> UserId:
        self._storage[user.id] = user
        return user.id

    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        return self._storage.get(user_id, None)


@lru_cache
def get_user_repository() -> UserRepositoryProtocol:
    return InMemoryUserRepository()


UserRepositoryDep = Annotated[UserRepositoryProtocol, Depends(get_user_repository)]
