from typing import Optional

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.funds.entity import Fund
from domain.funds.values import FundStatus
from infra.database.specification import OrderBySpecification, PaginationSpecification
from infra.models import FundModel
from infra.repositories.base import SQLAlchemyBaseRepository
from infra.repositories.dto.funds import FundOrmDTO


class SQLAlchemyFundRepository(SQLAlchemyBaseRepository[FundModel, Fund]):
    """Репозиторий для работы с остатками"""

    model = FundModel
    dto = FundOrmDTO

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_last_opened(self, user_id: str) -> Optional[Fund]:
        res = await self.find_one(
            OrderBySpecification(direction="desc", field="created_at"),
            PaginationSpecification(limit=1, offset=0),
            user_id=user_id,
            status=FundStatus.OPEN,
        )
        return res

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
