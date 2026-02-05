from typing import Optional, Annotated

from fastapi import Depends
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.accounts.entity import Account
from domain.accounts.repository import AccountRepositoryProtocol
from domain.accounts.values import Title, AccountId
from domain.users.values import UserId
from infra import SessionDep
from infra.models import AccountModel
from infra.repositories.base import BaseInMemoryRepository


class InMemoryAccountRepository(BaseInMemoryRepository[AccountId, Account]):

    def __init__(self):
        super().__init__()

    async def save(self, account: Account) -> AccountId:
        self._storage[account.id] = account
        return account.id

    async def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        return self._storage.get(account_id, None)

    async def get_by_user_id(self, user_id: UserId) -> list[Account]:
        return [
            account for account in self._storage.values() if account.user_id == user_id
        ]

    async def delete(self, account_id: AccountId) -> Optional[AccountId]:
        account = await self.get_by_id(account_id)
        if not account:
            return None
        self._storage.pop(account_id)
        return account_id

    async def count_by_user_id(self, user_id: UserId) -> int:
        return sum(1 for acc in self._storage.values() if acc.user_id == user_id)

    async def is_name_taken(self, user_id: UserId, name: Title) -> bool:
        return any(
            acc.name == name and acc.user_id == user_id
            for acc in self._storage.values()
        )

    async def update(self, account_id: AccountId, new_account: Account) -> None:
        await self.save(new_account)
        return


class PostgresAccountRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, account: Account) -> AccountId:
        acc = AccountModel(**account.to_dict())
        self._session.add(acc)
        await self._session.commit()
        return AccountId(acc.id)

    async def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        query = select(AccountModel).filter_by(id=account_id.value)
        account: AccountModel = await self._session.scalar(query)
        if not account:
            return None
        return self._to_domain(account)

    async def get_by_user_id(self, user_id: UserId) -> list[Account]:
        query = select(AccountModel).filter_by(user_id=user_id.value)
        accounts = await self._session.execute(query)
        return [self._to_domain(account) for account in accounts.scalars().all()]

    async def delete(self, account_id: AccountId) -> None:
        stmt = delete(AccountModel).filter_by(id=account_id.value)
        await self._session.execute(stmt)
        await self._session.commit()
        return

    async def count_by_user_id(self, user_id: UserId) -> int:
        query = (
            select(func.count())
            .select_from(AccountModel)
            .filter_by(user_id=user_id.value)
        )
        res = await self._session.scalar(query)
        return res or 0

    async def is_name_taken(self, user_id: UserId, name: Title) -> bool:
        query = (
            select(func.count())
            .select_from(AccountModel)
            .filter_by(user_id=user_id.value, name=name.value)
        )
        count = await self._session.scalar(query)
        return bool(count)

    async def update(self, account_id: AccountId, new_account: Account) -> None:
        update_data = new_account.to_dict()
        update_data.pop("user_id", None)

        stmt = update(AccountModel).filter_by(id=account_id.value).values(**update_data)
        await self._session.execute(stmt)
        await self._session.commit()
        await self._session.refresh(
            await self._session.get(AccountModel, account_id.value)
        )
        return

    @staticmethod
    def _to_domain(model: AccountModel) -> Account:
        return Account(
            id=AccountId(model.id),
            user_id=UserId(model.user_id),
            name=Title(model.name),
            type=model.type,
            currency=model.currency,
            balance=model.balance,
            created_at=model.created_at,
        )


def get_account_repository(session: SessionDep) -> AccountRepositoryProtocol:
    return PostgresAccountRepository(session)


AccountRepositoryDep = Annotated[
    AccountRepositoryProtocol, Depends(get_account_repository)
]
