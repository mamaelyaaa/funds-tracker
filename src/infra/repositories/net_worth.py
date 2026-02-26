from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.net_worth.repository import NetWorthRepositoryProtocol
from infra import SessionDep
from infra.models import AccountModel, HistoryModel


class PostgresNetWorthRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_total_balance(self, user_id: str) -> float:
        query = select(AccountModel).filter_by(user_id=user_id)
        accounts = await self._session.scalars(query)
        return sum(account.balance for account in accounts.all())

    async def get_user_incomes(
        self,
        user_id: str,
        # period: str,
        # start_date: datetime,
    ) -> float:

        query = (
            select(func.sum(HistoryModel.delta))
            .join(AccountModel, AccountModel.id == HistoryModel.account_id)
            .where(HistoryModel.delta > 0, AccountModel.user_id == user_id)
        )

        incomes = await self._session.scalar(query)
        return incomes

    async def get_user_expenses(
        self,
        user_id: str,
        # period: str,
        # start_date: datetime,
    ) -> float:

        query = (
            select(func.sum(HistoryModel.delta))
            .join(AccountModel, AccountModel.id == HistoryModel.account_id)
            .where(HistoryModel.delta < 0, AccountModel.user_id == user_id)
        )

        expenses = await self._session.scalar(query)
        return expenses


def get_net_worth_repository(session: SessionDep) -> NetWorthRepositoryProtocol:
    return PostgresNetWorthRepository(session)


NetWorthRepositoryDep = Annotated[
    NetWorthRepositoryProtocol, Depends(get_net_worth_repository)
]
