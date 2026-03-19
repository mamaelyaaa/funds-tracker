from sqlalchemy import delete, al
from sqlalchemy.ext.asyncio import AsyncSession

from domain.auth.entity import UserSession
from infra.models import UserSessionModel
from infra.repositories.base import SQLAlchemyBaseRepository
from infra.repositories.dto.user_sessions import UserSessionOrmDTO


class SQLAlchemyUserSessionRepository(
    SQLAlchemyBaseRepository[UserSessionModel, UserSession]
):
    """Репозиторий для работы с пользователями"""

    model = UserSessionModel
    dto = UserSessionOrmDTO

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def delete_many(
        self, sessions_ids: list[str], commit: bool, *specs, **filter_by
    ) -> None:
        stmt = delete(self.model).where(self.model.id.in_(sessions_ids))
        await self.session.execute(stmt)

        if commit:
            await self.session.commit()

        return
