from datetime import datetime
from typing import Optional, Annotated, Any

from fastapi import Depends
from sqlalchemy import select, desc, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.histories.entities import History
from domain.histories.protocols import HistoryRepositoryProtocol
from infra.database import SessionDep
from infra.models import HistoryModel
from infra.repositories.dto.histories import HistoryOrmDTO


class SQLAlchemyHistoryRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, history: History) -> str:
        history_model: HistoryModel = HistoryOrmDTO.from_entity_to_orm(history)
        self._session.add(history_model)
        await self._session.commit()
        return history_model.id

    async def get_by_id(self, history_id: str) -> Optional[History]:
        query = select(HistoryModel).filter_by(id=history_id)
        history = await self._session.scalar(query)
        return HistoryOrmDTO.from_orm_to_entity(history) if history else None

    async def get_last_history(self, account_id: str) -> Optional[History]:
        query = (
            select(HistoryModel)
            .filter_by(account_id=account_id)
            .order_by(HistoryModel.created_at.desc())
            .limit(1)
        )
        history = await self._session.scalar(query)
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

        res = await self._session.execute(query)
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
        history = await self._session.scalar(stmt)
        await self._session.commit()
        return HistoryOrmDTO.from_orm_to_entity(history) if history else None


def get_history_repository(session: SessionDep) -> HistoryRepositoryProtocol:
    return SQLAlchemyHistoryRepository(session)


HistoryRepositoryDep = Annotated[
    HistoryRepositoryProtocol, Depends(get_history_repository)
]
