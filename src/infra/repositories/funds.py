from typing import Any, Optional, Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.funds.entity import Fund
from domain.funds.protocol import FundRepositoryProtocol
from infra import SessionDep
from infra.models import FundModel
from infra.repositories.dto.funds import FundOrmDTO


class PostgresFundRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, fund: Fund) -> str:
        fund_model = FundOrmDTO.from_entity_to_orm(fund)
        self._session.add(fund_model)
        await self._session.commit()
        return fund_model.id

    async def update(
        self, user_id: str, fund_id: str, upd_data: dict[str, Any]
    ) -> Optional[Fund]:
        pass

    async def get_by_user_id(self, user_id: str, *args, **filter_by) -> Optional[Fund]:
        query = select(FundModel).filter_by(user_id=user_id, **filter_by)
        fund = await self._session.scalar(query)
        return fund

    async def get_last_opened(self, user_id: str) -> Optional[Fund]:
        pass


def get_fund_repository(session: SessionDep) -> FundRepositoryProtocol:
    return PostgresFundRepository(session)


FundRepositoryDep = Annotated[FundRepositoryProtocol, Depends(get_fund_repository)]
