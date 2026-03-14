from datetime import datetime
from typing import Optional, Any

from sqlalchemy import select, desc, func, update, between
from sqlalchemy.ext.asyncio import AsyncSession

from domain.histories.entities import History
from infra.models import HistoryModel, AccountModel
from infra.repositories.base import SQLAlchemyBaseRepository
from infra.repositories.dto.histories import HistoryOrmDTO


class SQLAlchemyHistoryRepository(SQLAlchemyBaseRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def save(self, history: History, commit: bool = True) -> str:
        history_model: HistoryModel = HistoryOrmDTO.from_entity_to_orm(history)
        self.session.add(history_model)

        if commit:
            await self.session.commit()

        return history_model.id

    async def get_by_id(self, history_id: str) -> Optional[History]:
        query = select(HistoryModel).filter_by(id=history_id)
        history = await self.session.scalar(query)
        return HistoryOrmDTO.from_orm_to_entity(history) if history else None

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
        period: str,
        start_date: datetime,
        limit: Optional[int] = None,
        asc: bool = True,
    ) -> list[History]:

        subq = (
            select(
                func.max(HistoryModel.created_at).label("last_date"),
                func.date_trunc(period, HistoryModel.created_at).label("trunc_date"),
            )
            .group_by("trunc_date")
            .order_by(desc("trunc_date"))
            .subquery()
        )

        query = (
            select(HistoryModel)
            .filter_by(account_id=account_id)
            .join(subq, HistoryModel.created_at == subq.c.last_date)
            .where(HistoryModel.created_at >= start_date)
            .order_by(
                HistoryModel.created_at.desc() if not asc else HistoryModel.created_at
            )
        )
        if limit:
            query = query.limit(limit)

        res = await self.session.execute(query)
        return [HistoryOrmDTO.from_orm_to_entity(row) for row in res.scalars().all()]

    async def update(
        self, history_id: str, upd_data: dict[str, Any]
    ) -> Optional[History]:
        stmt = (
            update(HistoryModel)
            .filter_by(id=history_id)
            .values(**upd_data)
            .returning(HistoryModel)
        )
        history = await self.session.scalar(stmt)
        await self.session.commit()
        return HistoryOrmDTO.from_orm_to_entity(history) if history else None

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
