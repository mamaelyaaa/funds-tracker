from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users.entity import User
from infra.models import UserModel
from infra.repositories.base import SQLAlchemyBaseRepository
from infra.repositories.dto.users import UserOrmDTO


class SQLAlchemyUserRepository(SQLAlchemyBaseRepository[UserModel, User]):
    model = UserModel
    dto = UserOrmDTO

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    # async def save(self, user: User) -> str:
    #     user_model = UserOrmDTO.from_entity_to_orm(user)
    #     self.session.add(user_model)
    #     await self.session.commit()
    #     return user_model.id

    async def get_by_id(self, user_id: str) -> Optional[User]:
        query = select(UserModel).filter_by(id=user_id)
        user = await self.session.scalar(query)
        return UserOrmDTO.from_orm_to_entity(user) if user else None
