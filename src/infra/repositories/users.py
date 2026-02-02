from typing import Optional, Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users.entity import User
from domain.users.repository import UserRepositoryProtocol
from domain.users.values import UserId
from infra import SessionDep
from infra.models import UserModel
from infra.repositories.base import BaseInMemoryRepository


class InMemoryUserRepository(BaseInMemoryRepository[UserId, User]):

    def __init__(self):
        super().__init__()

    async def save(self, user: User) -> UserId:
        self._storage[user.id] = user
        return user.id

    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        return self._storage.get(user_id, None)


class SQLAUserRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> UserId:
        user_model = UserModel(
            id=user.id.value,
            name=user.name,
            created_at=user.created_at,
        )
        self._session.add(user_model)
        await self._session.commit()
        return user.id

    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        query = select(UserModel).filter_by(id=user_id.value)
        res = await self._session.execute(query)
        return res.scalar_one_or_none()


def get_user_repository(session: SessionDep) -> UserRepositoryProtocol:
    return SQLAUserRepository(session)


UserRepositoryDep = Annotated[UserRepositoryProtocol, Depends(get_user_repository)]
