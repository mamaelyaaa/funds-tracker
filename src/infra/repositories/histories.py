from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, Annotated

from fastapi import Depends
from sqlalchemy import select, desc, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.accounts.values import AccountId
from domain.histories.entities import History
from domain.histories.repository import HistoryRepositoryProtocol
from domain.histories.values import HistoryId
from infra.database import SessionDep
from infra.models import HistoryModel
from infra.repositories.base import BaseInMemoryRepository


class InMemoryHistoryRepository(BaseInMemoryRepository[HistoryId, History]):
    def __init__(self):
        super().__init__()
        self._account_index: dict[AccountId, list[History]] = defaultdict(list)

    async def save(self, history: History) -> HistoryId:
        self._storage[history.id] = history
        self._account_index[history.account_id].append(history)
        return history.id

    async def get_by_id(self, history_id: HistoryId) -> Optional[History]:
        return self._storage.get(history_id, None)

    async def get_history_linked_to_period(
        self, account_id: AccountId, period: str, start_date: datetime
    ) -> list[History]:

        account_histories = self._account_index.get(account_id, [])
        filtered = [h for h in account_histories if h.created_at >= start_date]

        if not filtered:
            return []

        period_groups: dict[datetime, History] = {}

        for history in filtered:
            trunc_date = self._truncate_datetime(history.created_at, period)

            if (
                trunc_date not in period_groups
                or history.created_at > period_groups[trunc_date].created_at
            ):
                period_groups[trunc_date] = history

        result = list(period_groups.values())
        result.sort(key=lambda x: x.created_at, reverse=True)

        return result

    @staticmethod
    def _truncate_datetime(dt: datetime, period: str) -> datetime:
        if period == "minute":
            return dt.replace(second=0, microsecond=0)
        elif period == "hour":
            return dt.replace(minute=0, second=0, microsecond=0)
        elif period == "day":
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            days_since_monday = dt.weekday()
            start_of_week = dt - timedelta(days=days_since_monday)
            return start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "month":
            return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    async def update(self, history_id: HistoryId, new_history: History) -> History:
        await self.save(new_history)
        return new_history

    async def get_acc_by_acc_id_with_time_limit(
        self, account_id: AccountId, time_limit: timedelta
    ) -> Optional[History]:
        history: list[History] = [
            hist for hist in self._storage.values() if hist.account_id == account_id
        ]
        res: list[History] = []

        for row in history:
            if datetime.now() - row.created_at < time_limit:
                res.append(row)

        return res[-1] if res else None


class PostgresHistoryRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, history: History) -> HistoryId:
        history_model = HistoryModel(
            id=history.id.value,
            balance=history.balance,
            account_id=history.account_id.value,
            created_at=history.created_at,
        )
        self._session.add(history_model)
        await self._session.commit()
        return history.id

    async def get_by_id(self, history_id: HistoryId) -> Optional[History]:
        query = select(HistoryModel).filter_by(id=history_id.value)
        res = await self._session.scalar(query)
        return res

    async def get_history_linked_to_period(
        self,
        account_id: AccountId,
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
            .filter_by(account_id=account_id.value)
            .join(subq, HistoryModel.created_at == subq.c.last_date)
            .where(HistoryModel.created_at >= start_date)
            .order_by(
                HistoryModel.created_at.desc() if not asc else HistoryModel.created_at
            )
        )
        if limit:
            query = query.limit(limit)

        res = await self._session.execute(query)
        return [self._to_domain(row) for row in res.scalars().all()]

    async def update(self, history_id: HistoryId, new_history: History) -> History:
        stmt = (
            update(HistoryModel)
            .filter_by(id=history_id.value)
            .values(
                balance=new_history.balance,
                created_at=new_history.created_at,
            )
            .returning(HistoryModel)
        )
        res = await self._session.execute(stmt)
        await self._session.commit()
        return self._to_domain(res.scalar_one())

    async def get_acc_by_acc_id_with_time_limit(
        self, account_id: AccountId, time_limit: timedelta
    ) -> Optional[History]:
        query = (
            select(HistoryModel)
            .filter_by(account_id=account_id.value)
            .where(
                datetime.now() - HistoryModel.created_at < time_limit,
            )
            .order_by(HistoryModel.created_at.desc())
            .limit(1)
        )
        history = await self._session.scalar(query)
        return self._to_domain(history) if history else None

    @staticmethod
    def _to_domain(model: HistoryModel) -> History:
        return History(
            id=HistoryId(model.id),
            account_id=AccountId(model.account_id),
            balance=model.balance,
            created_at=model.created_at,
        )


def get_history_repository(session: SessionDep) -> HistoryRepositoryProtocol:
    return PostgresHistoryRepository(session)


HistoryRepositoryDep = Annotated[
    HistoryRepositoryProtocol, Depends(get_history_repository)
]
