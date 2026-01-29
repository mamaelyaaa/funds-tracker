from typing import Optional, Annotated

from fastapi import Depends
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.domain import AccountId, Account
from accounts.repository import AccountRepositoryProtocol
from accounts.values import Title
from infra.database import SessionDep
from infra.models import AccountModel
from users.values import UserId


class InMemoryAccountRepository:

    def __init__(self):
        self._storage: dict[AccountId, Account] = {}

    async def save(self, account: Account) -> AccountId:
        self._storage[account.id] = account
        return account.id

    async def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        return self._storage.get(account_id, None)

    async def delete(self, account_id: AccountId) -> None:
        self._storage.pop(account_id)

    async def count_by_user_id(self, user_id: UserId) -> int:
        return sum(1 for acc in self._storage.values() if acc.user_id == user_id)

    async def is_name_taken(self, user_id: UserId, name: Title) -> bool:
        return any(
            acc.name == name.value and acc.user_id == user_id
            for acc in self._storage.values()
        )

    async def update(self, account_id: AccountId, new_account: Account) -> None:
        raise NotImplemented


class SQLAAccountRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, account: Account) -> AccountId:
        acc = AccountModel(**account.model_dump())
        self.session.add(acc)
        await self.session.commit()
        return AccountId(acc.id)

    async def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        query = select(AccountModel).filter_by(id=account_id.value)
        account: AccountModel = await self.session.scalar(query)
        if not account:
            return None
        return self._to_domain(account)

    async def get_by_user_id(self, user_id: UserId) -> list[Account]:
        query = select(AccountModel).filter_by(user_id=user_id.value)
        accounts = await self.session.execute(query)
        return [self._to_domain(account) for account in accounts.scalars().all()]

    async def delete(self, account_id: AccountId) -> None:
        stmt = delete(AccountModel).filter_by(id=account_id.value)
        await self.session.execute(stmt)
        await self.session.commit()
        return

    async def count_by_user_id(self, user_id: UserId) -> int:
        query = (
            select(func.count())
            .select_from(AccountModel)
            .filter_by(user_id=user_id.value)
        )
        res = await self.session.scalar(query)
        return res or 0

    async def is_name_taken(self, user_id: UserId, name: Title) -> bool:
        query = (
            select(func.count())
            .select_from(AccountModel)
            .filter_by(user_id=user_id.value, name=name.value)
        )
        count = await self.session.scalar(query)
        return bool(count)

    async def update(self, account_id: AccountId, new_account: Account) -> None:
        stmt = (
            update(AccountModel)
            .filter_by(id=account_id.value)
            .values(**new_account.model_dump())
        )
        await self.session.execute(stmt)
        await self.session.commit()
        await self.session.refresh(
            await self.session.get(AccountModel, account_id.value)
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
    return SQLAAccountRepository(session)


AccountRepositoryDep = Annotated[
    AccountRepositoryProtocol, Depends(get_account_repository)
]
