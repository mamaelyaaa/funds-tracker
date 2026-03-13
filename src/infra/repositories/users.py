from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users.entity import User
from infra.models import UserModel
from infra.repositories.dto.users import UserOrmDTO


class SQLAlchemyUserRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> str:
        user_model = UserOrmDTO.from_entity_to_orm(user)
        self._session.add(user_model)
        await self._session.commit()
        return user_model.id

    async def get_by_id(self, user_id: str) -> Optional[User]:
        query = select(UserModel).filter_by(id=user_id)
        user = await self._session.scalar(query)
        return UserOrmDTO.from_orm_to_entity(user) if user else None
