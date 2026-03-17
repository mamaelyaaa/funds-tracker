from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.accounts.entity import Account
from infra.models import AccountModel
from .base import SQLAlchemyBaseRepository
from .dto.accounts import AccountOrmDTO


class SQLAlchemyAccountRepository(SQLAlchemyBaseRepository[AccountModel, Account]):
    """Репозиторий работы со счетами"""

    model = AccountModel
    dto = AccountOrmDTO

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def count_by_user_id(self, user_id: str) -> int:
        query = (
            select(func.count()).select_from(AccountModel).filter_by(user_id=user_id)
        )
        res = await self.session.scalar(query)
        return res or 0

    async def is_name_taken(self, user_id: str, name: str) -> bool:
        query = (
            select(func.count())
            .select_from(AccountModel)
            .filter_by(user_id=user_id, name=name)
        )
        count = await self.session.scalar(query)
        return bool(count)

    async def check_exists_by_id(self, user_id: str, account_id: str) -> bool:
        query = (
            select(func.count())
            .select_from(AccountModel)
            .filter_by(user_id=user_id, id=account_id)
        )
        res = await self.session.scalar(query)
        return bool(res)
