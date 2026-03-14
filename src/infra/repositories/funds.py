from typing import Any, Optional, Annotated

from fastapi import Depends
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.funds.entity import Fund
from domain.funds.protocol import FundRepositoryProtocol
from domain.funds.values import FundStatus
from infra import SessionDep
from infra.models import FundModel
from infra.repositories.dto.funds import FundOrmDTO


class SQLAlchemyFundRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, fund: Fund) -> str:
        fund_model = FundOrmDTO.from_entity_to_orm(fund)
        self._session.add(fund_model)
        await self._session.commit()
        return fund_model.id

    async def update(
        self, user_id: str, fund_id: str, upd_data: dict[str, Any], commit: bool = True
    ) -> Optional[Fund]:
        stmt = (
            update(FundModel)
            .filter_by(user_id=user_id, id=fund_id)
            .values(**upd_data)
            .returning(FundModel)
        )
        fund = await self._session.scalar(stmt)
        if commit:
            await self._session.commit()
        else:
            await self._session.flush()

        return FundOrmDTO.from_orm_to_entity(fund) if fund else None

    async def get_by_user_id(self, user_id: str, *args, **filter_by) -> Optional[Fund]:
        query = select(FundModel).filter_by(user_id=user_id, **filter_by)
        fund = await self._session.scalar(query)
        return FundOrmDTO.from_orm_to_entity(fund) if fund else None

    async def get_by_id(self, fund_id: str) -> Optional[Fund]:
        query = select(FundModel).filter_by(id=fund_id)
        fund = await self._session.scalar(query)
        return FundOrmDTO.from_orm_to_entity(fund) if fund else None

    async def get_last_opened(self, user_id: str) -> Optional[Fund]:
        query = (
            select(FundModel)
            .filter_by(user_id=user_id, status=FundStatus.OPEN)
            .order_by(FundModel.created_at.desc())
            .limit(1)
        )
        last_fund = await self._session.scalar(query)
        return FundOrmDTO.from_orm_to_entity(last_fund) if last_fund else None

    async def get_last_closed(self, user_id: str) -> Optional[Fund]:
        query = (
            select(FundModel)
            .filter_by(user_id=user_id, status=FundStatus.CLOSED)
            .order_by(FundModel.created_at.desc())
            .limit(1)
        )
        last_fund = await self._session.scalar(query)
        return FundOrmDTO.from_orm_to_entity(last_fund) if last_fund else None

    async def get_unopened(self, user_id: str) -> list[Fund]:
        query = (
            select(FundModel)
            .filter_by(user_id=user_id)
            .where(
                or_(
                    FundModel.status == FundStatus.CLOSED,
                    FundModel.status == FundStatus.DISTRIBUTED,
                )
            )
            .order_by(FundModel.end_date.desc())
        )
        funds = await self._session.scalars(query)
        return [FundOrmDTO.from_orm_to_entity(fund) for fund in funds]


def get_fund_repository(session: SessionDep) -> FundRepositoryProtocol:
    return SQLAlchemyFundRepository(session)


FundRepositoryDep = Annotated[FundRepositoryProtocol, Depends(get_fund_repository)]
