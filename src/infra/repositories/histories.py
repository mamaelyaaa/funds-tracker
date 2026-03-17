from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, between
from sqlalchemy.ext.asyncio import AsyncSession

from domain.histories.entities import History
from infra.models import HistoryModel, AccountModel
from infra.repositories.base import SQLAlchemyBaseRepository
from infra.repositories.dto.histories import HistoryOrmDTO


class SQLAlchemyHistoryRepository(SQLAlchemyBaseRepository[HistoryModel, History]):
    """Репозиторий для работы с историей счетов"""

    model = HistoryModel
    dto = HistoryOrmDTO

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_last_history(self, account_id: str) -> Optional[History]:
        query = (
            select(HistoryModel)
            .filter_by(account_id=account_id)
            .order_by(HistoryModel.created_at.desc())
            .limit(1)
        )
        history = await self.session.scalar(query)
        return HistoryOrmDTO.from_orm_to_entity(history) if history else None

    async def get_history_linked_to_period(
        self,
        account_id: str,
        *specs,
    ) -> list[History]:

        query = select(HistoryModel).filter_by(account_id=account_id)
        query = self._apply_specs(query, specs)

        res = await self.session.execute(query)
        return [HistoryOrmDTO.from_orm_to_entity(row) for row in res.scalars().all()]

    async def get_sum_delta_in_period(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> int:
        query = (
            select(func.sum(HistoryModel.delta))
            .join(HistoryModel.account)
            .filter_by(user_id=user_id)
            .filter(
                between(HistoryModel.created_at, start_date, end_date),
            )
        )
        res = await self.session.scalar(query)
        return res or 0

    async def get_first_history_date_by_user(self, user_id: str) -> Optional[datetime]:
        query = (
            select(HistoryModel.created_at)
            .join(HistoryModel.account)
            .filter(AccountModel.user_id == user_id)
            .order_by(HistoryModel.created_at.asc())
            .limit(1)
        )
        res = await self.session.scalar(query)
        return HistoryOrmDTO.ensure_utc(res) if res else None
