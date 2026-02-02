from typing import Optional, Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infra.database import SessionDep
from infra.models import SavingsHistoryModel
from domain.savings.domain import SavingsHistory
from domain.savings.repository import SavingsHistoryRepositoryProtocol
from domain.savings.values import SavingsId
from infra.repositories.base import BaseInMemoryRepository


class InMemorySavingsHistoryRepository(
    BaseInMemoryRepository[SavingsId, SavingsHistory]
):

    def __init__(self):
        super().__init__()

    async def save(self, savings: SavingsHistory) -> SavingsId:
        self._storage[savings.id] = savings
        return savings.id

    async def get_by_id(self, savings_id: SavingsId) -> Optional[SavingsHistory]:
        return self._storage.get(savings_id, None)


class SQLASavingsHistoryRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, savings: SavingsHistory) -> SavingsId:
        savings_model = SavingsHistoryModel(
            id=savings.id.value,
            balance=savings.balance,
            account_id=savings.account_id.value,
            created_at=savings.created_at,
        )
        self._session.add(savings_model)
        await self._session.commit()
        return savings.id

    async def get_by_id(self, savings_id: SavingsId) -> Optional[SavingsHistory]:
        query = select(SavingsHistoryModel).filter_by(id=savings_id.value)
        res = await self._session.scalar(query)
        return res


def get_savings_repository(session: SessionDep) -> SavingsHistoryRepositoryProtocol:
    return SQLASavingsHistoryRepository(session)


SavingsRepositoryDep = Annotated[
    SavingsHistoryRepositoryProtocol, Depends(get_savings_repository)
]
