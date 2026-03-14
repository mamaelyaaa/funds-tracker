from decimal import Decimal
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from domain.funds.entity import FundDistribution
from domain.funds.protocol import FundDistRepositoryProtocol
from domain.funds.values import FundReserveType
from infra import SessionDep
from infra.models import AccountModel, GoalModel, Base
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
        reserve = await self._session.scalar(query)
        if not reserve:
            return

        if reserve_type == FundReserveType.ACCOUNT:
            reserve.balance += balance
        elif reserve_type == FundReserveType.GOAL:
            reserve.current_amount += balance

        await self._session.commit()
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


def get_fund_dist_repository(session: SessionDep) -> FundDistRepositoryProtocol:
    return SQLAlchemyFundDistRepository(session)


FundDistRepositoryDep = Annotated[
    FundDistRepositoryProtocol, Depends(get_fund_dist_repository)
]
