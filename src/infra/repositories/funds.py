from typing import Any, Optional

from sqlalchemy import select, update, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.funds.entity import Fund
from domain.funds.values import FundStatus
from infra.models import FundModel
from infra.repositories.base import SQLAlchemyBaseRepository
from infra.repositories.dto.funds import FundOrmDTO


class SQLAlchemyFundRepository(SQLAlchemyBaseRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def save(self, fund: Fund) -> str:
        fund_model = FundOrmDTO.from_entity_to_orm(fund)
        self.session.add(fund_model)
        await self.session.commit()
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
        fund = await self.session.scalar(stmt)
        if commit:
            await self.session.commit()
        else:
            await self.session.flush()

        return FundOrmDTO.from_orm_to_entity(fund) if fund else None

    async def get_by_user_id(self, user_id: str, *args, **filter_by) -> Optional[Fund]:
        query = select(FundModel).filter_by(user_id=user_id, **filter_by)
        fund = await self.session.scalar(query)
        return FundOrmDTO.from_orm_to_entity(fund) if fund else None

    async def get_by_id(self, fund_id: str) -> Optional[Fund]:
        query = select(FundModel).filter_by(id=fund_id)
        fund = await self.session.scalar(query)
        return FundOrmDTO.from_orm_to_entity(fund) if fund else None

    async def get_last_opened(self, user_id: str) -> Optional[Fund]:
        query = (
            select(FundModel)
            .filter_by(user_id=user_id, status=FundStatus.OPEN)
            .order_by(FundModel.created_at.desc())
            .limit(1)
        )
        last_fund = await self.session.scalar(query)
        return FundOrmDTO.from_orm_to_entity(last_fund) if last_fund else None

    async def get_last_unopened(self, user_id: str) -> Optional[Fund]:
        query = (
            select(FundModel)
            .filter_by(user_id=user_id)
            .where(
                or_(
                    FundModel.status == FundStatus.CLOSED,
                    FundModel.status == FundStatus.DISTRIBUTED,
                )
            )
            .order_by(FundModel.created_at.desc())
            .limit(1)
        )
        last_fund = await self.session.scalar(query)
        return FundOrmDTO.from_orm_to_entity(last_fund) if last_fund else None

    async def get_unopened(self, user_id: str, *specs) -> list[Fund]:
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
        query = self._apply_specs(query, specs)

        funds = await self.session.scalars(query)
        return [FundOrmDTO.from_orm_to_entity(fund) for fund in funds]

    async def get_count_by_user_id(self, user_id: str) -> int:
        query = select(func.count()).select_from(FundModel).filter_by(user_id=user_id)
        res = await self.session.scalar(query)
        return res or 0
