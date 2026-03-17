from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users.entity import User
from infra.models import UserModel
from infra.repositories.base import SQLAlchemyBaseRepository
from infra.repositories.dto.users import UserOrmDTO


class SQLAlchemyUserRepository(SQLAlchemyBaseRepository[UserModel, User]):
    """Репозиторий для работы с пользователями"""

    model = UserModel
    dto = UserOrmDTO

    def __init__(self, session: AsyncSession):
        super().__init__(session)
