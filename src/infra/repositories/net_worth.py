from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.net_worth.repository import NetWorthRepositoryProtocol
from domain.users.values import UserId
from infra import SessionDep
from infra.models import AccountModel


class PostgresNetWorthRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_total_balance(self, user_id: UserId) -> float:
        query = select(AccountModel).filter_by(user_id=user_id.as_generic_type())
        accounts = await self._session.scalars(query)
        return sum(account.balance for account in accounts.all())


def get_net_worth_repository(session: SessionDep) -> NetWorthRepositoryProtocol:
    return PostgresNetWorthRepository(session)


NetWorthRepositoryDep = Annotated[
    NetWorthRepositoryProtocol, Depends(get_net_worth_repository)
]
