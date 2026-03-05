from typing import Optional, Annotated, Any

from fastapi import Depends
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.accounts.entity import Account
from domain.accounts.protocols import AccountRepositoryProtocol
from infra import SessionDep
from infra.models import AccountModel
from .dto.accounts import AccountOrmDTO


class SQLAlchemyAccountRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, account: Account) -> str:
        acc: AccountModel = AccountOrmDTO.from_entity_to_orm(account)
        self._session.add(acc)
        await self._session.commit()
        return acc.id

    async def get_by_id(self, user_id: str, account_id: str) -> Optional[Account]:
        query = select(AccountModel).filter_by(id=account_id, user_id=user_id)
        account = await self._session.scalar(query)
        return AccountOrmDTO.from_orm_to_entity(account) if account else None

    async def get_by_user_id(self, user_id: str) -> list[Account]:
        query = select(AccountModel).filter_by(user_id=user_id)
        accounts = await self._session.scalars(query)
        return [AccountOrmDTO.from_orm_to_entity(account) for account in accounts.all()]

    async def delete(self, user_id: str, account_id: str) -> None:
        stmt = delete(AccountModel).filter_by(id=account_id, user_id=user_id)
        await self._session.execute(stmt)
        await self._session.commit()
        return

    async def count_by_user_id(self, user_id: str) -> int:
        query = (
            select(func.count()).select_from(AccountModel).filter_by(user_id=user_id)
        )
        res = await self._session.scalar(query)
        return res or 0

    async def is_name_taken(self, user_id: str, name: str) -> bool:
        query = (
            select(func.count())
            .select_from(AccountModel)
            .filter_by(user_id=user_id, name=name)
        )
        count = await self._session.scalar(query)
        return bool(count)

    async def update(
        self, user_id: str, account_id: str, upd_data: dict[str, Any]
    ) -> Optional[Account]:
        stmt = (
            update(AccountModel)
            .filter_by(id=account_id, user_id=user_id)
            .values(**upd_data)
            .returning(AccountModel)
        )
        res = await self._session.execute(stmt)
        await self._session.commit()
        return res.scalar_one_or_none()


def get_account_repository(session: SessionDep) -> AccountRepositoryProtocol:
    return SQLAlchemyAccountRepository(session)


AccountRepositoryDep = Annotated[
    AccountRepositoryProtocol, Depends(get_account_repository)
]
