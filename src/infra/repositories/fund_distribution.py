from sqlalchemy.ext.asyncio import AsyncSession

from domain.funds.entity import FundDistribution
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
