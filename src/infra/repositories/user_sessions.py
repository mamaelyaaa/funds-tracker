from datetime import datetime

from sqlalchemy import delete
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

    async def delete_expired_by_user(
        self, user_id: str, expired_before: datetime, commit: bool
    ) -> None:
        stmt = delete(UserSessionModel).where(
            UserSessionModel.user_id == user_id,
            UserSessionModel.expires_in < expired_before,
        )
        await self.session.execute(stmt)
        if commit:
            await self.session.commit()
        return
