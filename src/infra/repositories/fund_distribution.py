from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.funds.entity import FundDistribution
from domain.funds.protocol import FundDistRepositoryProtocol
from infra import SessionDep
from infra.models.funds import FundDistributionModel
from infra.repositories.dto.fund_distribution import FundDistOrmDTO


class SQLAlchemyFundDistRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_all(self, fund_dists: list[FundDistribution], commit: bool) -> None:
        fund_dists_models = [
            FundDistOrmDTO.from_entity_to_orm(fund_dist) for fund_dist in fund_dists
        ]

        self._session.add_all(fund_dists_models)

        if commit:
            await self._session.commit()
        else:
            await self._session.flush()

        return

    async def get_by_find_id(self, fund_id: str) -> list[FundDistribution]:
        query = select(FundDistributionModel).filter_by(fund_id=fund_id)
        fund_dists = await self._session.scalars(query)
        return [
            FundDistOrmDTO.from_orm_to_entity(fund_dist)
            for fund_dist in fund_dists.all()
        ]


def get_fund_dist_repository(session: SessionDep) -> FundDistRepositoryProtocol:
    return SQLAlchemyFundDistRepository(session)


FundDistRepositoryDep = Annotated[
    FundDistRepositoryProtocol, Depends(get_fund_dist_repository)
]
