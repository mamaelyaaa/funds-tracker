from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.funds.entity import FundDistribution
from domain.funds.values import FundReserveType
from infra.models import AccountModel, GoalModel
from infra.models.funds import FundDistributionModel
from infra.repositories.base import SQLAlchemyBaseRepository
from infra.repositories.dto.fund_distribution import FundDistOrmDTO


class SQLAlchemyFundDistRepository(
    SQLAlchemyBaseRepository[FundDistribution, FundDistributionModel]
):
    """Репозиторий для работы с распределением остатков"""

    model = FundDistributionModel
    dto = FundDistOrmDTO

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def save_all(
        self, fund_dists: list[FundDistribution], commit: bool = True
    ) -> None:
        fund_dists_models = [
            FundDistOrmDTO.from_entity_to_orm(fund_dist) for fund_dist in fund_dists
        ]

        self.session.add_all(fund_dists_models)

        if commit:
            await self.session.commit()

        return

    async def get_by_find_id(self, fund_id: str) -> list[FundDistribution]:
        query = select(FundDistributionModel).filter_by(fund_id=fund_id)
        fund_dists = await self.session.scalars(query)
        return [
            FundDistOrmDTO.from_orm_to_entity(fund_dist)
            for fund_dist in fund_dists.all()
        ]

    async def update_reserve_with_accumulate(
        self,
        reserve_type: FundReserveType,
        user_id: str,
        reserve_id: str,
        balance: Decimal,
    ) -> None:

        model, model_balance = await self._select_model_balance(reserve_type)

        query = (
            select(model_balance)
            .select_from(model)
            .filter_by(id=reserve_id, user_id=user_id)
        )
        reserve = await self.session.scalar(query)
        if not reserve:
            return

        if reserve_type == FundReserveType.ACCOUNT:
            reserve.balance += balance
        elif reserve_type == FundReserveType.GOAL:
            reserve.current_amount += balance

        return

    @staticmethod
    async def _select_model_balance(reserve_type: FundReserveType):
        if reserve_type == FundReserveType.ACCOUNT:
            model = AccountModel
            return model, model.balance
        elif reserve_type == FundReserveType.GOAL:
            model = GoalModel
            return model, model.current_amount
        else:
            raise
