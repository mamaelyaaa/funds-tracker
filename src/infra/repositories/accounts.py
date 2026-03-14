from typing import Optional, Any

from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.accounts.entity import Account
from infra.database.specification import SpecificationProtocol
from infra.models import AccountModel
from .base import SQLAlchemyBaseRepository
from .dto.accounts import AccountOrmDTO


class SQLAlchemyAccountRepository(SQLAlchemyBaseRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def save(self, account: Account) -> str:
        acc: AccountModel = AccountOrmDTO.from_entity_to_orm(account)
        self.session.add(acc)
        await self.session.commit()
        return acc.id

    async def get_by_id(self, user_id: str, account_id: str) -> Optional[Account]:
        query = select(AccountModel).filter_by(id=account_id, user_id=user_id)
        account = await self.session.scalar(query)
        return AccountOrmDTO.from_orm_to_entity(account) if account else None

    async def get_by_user_id(
        self, user_id: str, *specs: SpecificationProtocol
    ) -> list[Account]:
        query = select(AccountModel).filter_by(user_id=user_id)
        query = self._apply_specs(query, specs)

        accounts = await self.session.scalars(query)
        return [AccountOrmDTO.from_orm_to_entity(account) for account in accounts.all()]

    async def delete(self, user_id: str, account_id: str) -> None:
        stmt = delete(AccountModel).filter_by(id=account_id, user_id=user_id)
        await self.session.execute(stmt)
        await self.session.commit()
        return

    async def count_by_user_id(self, user_id: str) -> int:
        query = (
            select(func.count()).select_from(AccountModel).filter_by(user_id=user_id)
        )
        res = await self.session.scalar(query)
        return res or 0

    async def is_name_taken(self, user_id: str, name: str) -> bool:
        query = (
            select(func.count())
            .select_from(AccountModel)
            .filter_by(user_id=user_id, name=name)
        )
        count = await self.session.scalar(query)
        return bool(count)

    async def update(
        self,
        user_id: str,
        account_id: str,
        upd_data: dict[str, Any],
        commit: bool = True,
    ) -> Optional[Account]:
        stmt = (
            update(AccountModel)
            .filter_by(id=account_id, user_id=user_id)
            .values(**upd_data)
            .returning(AccountModel)
        )
        account = await self.session.scalar(stmt)

        if commit:
            await self.session.commit()

        return AccountOrmDTO.from_orm_to_entity(account) if account else None

    async def check_exists_by_id(self, user_id: str, account_id: str) -> bool:
        query = (
            select(func.count())
            .select_from(AccountModel)
            .filter_by(user_id=user_id, id=account_id)
        )
        res = await self.session.scalar(query)
        return bool(res)
