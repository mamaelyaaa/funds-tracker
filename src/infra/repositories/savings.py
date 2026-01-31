from functools import lru_cache
from typing import Optional, Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infra.database import SessionDep
from infra.models import SavingsHistoryModel
from savings.domain import SavingsHistory
from savings.repository import SavingsHistoryRepositoryProtocol
from savings.values import SavingsId


class InMemorySavingsHistoryRepository:

    def __init__(self):
        self._storage: dict[SavingsId, SavingsHistory] = {}

    async def save(self, savings: SavingsHistory) -> SavingsId:
        self._storage[savings.id] = savings
        return savings.id

    async def get_by_id(self, savings_id: SavingsId) -> Optional[SavingsHistory]:
        return self._storage.get(savings_id, None)


class SQLASavingsHistoryRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, savings: SavingsHistory) -> SavingsId:
        savings_model = SavingsHistoryModel(
            id=savings.id.value,
            balance=savings.balance,
            account_id=savings.account_id.value,
            created_at=savings.created_at,
        )
        self.session.add(savings_model)
        await self.session.commit()
        return savings.id

    async def get_by_id(self, savings_id: SavingsId) -> Optional[SavingsHistory]:
        query = select(SavingsHistoryModel).filter_by(id=savings_id.value)
        res = await self.session.scalar(query)
        return res


def get_savings_repository(session: SessionDep) -> SavingsHistoryRepositoryProtocol:
    return SQLASavingsHistoryRepository(session)


SavingsRepositoryDep = Annotated[
    SavingsHistoryRepositoryProtocol, Depends(get_savings_repository)
]
