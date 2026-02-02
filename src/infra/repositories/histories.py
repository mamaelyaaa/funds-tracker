from typing import Optional, Annotated

from fastapi import Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from domain.accounts.values import AccountId
from infra.database import SessionDep
from infra.models import SavingsHistoryModel
from domain.histories.domain import AccountHistory
from domain.histories.repository import HistoryRepositoryProtocol
from domain.histories.values import SavingsId
from infra.repositories.base import BaseInMemoryRepository


class InMemorySavingsHistoryRepository(
    BaseInMemoryRepository[SavingsId, AccountHistory]
):

    def __init__(self):
        super().__init__()

    async def save(self, savings: AccountHistory) -> SavingsId:
        self._storage[savings.id] = savings
        return savings.id

    async def get_by_id(self, savings_id: SavingsId) -> Optional[AccountHistory]:
        return self._storage.get(savings_id, None)


class SQLASavingsHistoryRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, savings: AccountHistory) -> SavingsId:
        savings_model = SavingsHistoryModel(
            id=savings.id.value,
            balance=savings.balance,
            account_id=savings.account_id.value,
            created_at=savings.created_at,
        )
        self._session.add(savings_model)
        await self._session.commit()
        return savings.id

    async def get_by_id(self, savings_id: SavingsId) -> Optional[AccountHistory]:
        query = select(SavingsHistoryModel).filter_by(id=savings_id.value)
        res = await self._session.scalar(query)
        return res

    async def get_by_acc_id(
        self,
        account_id: AccountId,
        order_by: str = "id",
        asc: bool = True,
        limit: int = 10,
        offset: int = 0,
    ) -> list[AccountHistory]:
        query = (
            select(SavingsHistoryModel)
            .filter_by(account_id=account_id.value)
            .order_by(desc(order_by) if not asc else order_by)
            .limit(limit)
            .offset(offset)
        )
        res = await self._session.scalars(query)
        return [self._to_domain(row) for row in res.all()]

    @staticmethod
    def _to_domain(model: SavingsHistoryModel) -> AccountHistory:
        return AccountHistory(
            account_id=AccountId(model.account_id),
            balance=model.balance,
            created_at=model.created_at,
        )


def get_history_repository(session: SessionDep) -> HistoryRepositoryProtocol:
    return SQLASavingsHistoryRepository(session)


HistoryRepositoryDep = Annotated[
    HistoryRepositoryProtocol, Depends(get_history_repository)
]
