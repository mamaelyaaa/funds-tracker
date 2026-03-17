from decimal import Decimal
from typing import Protocol, Optional

from domain.funds.entity import Fund, FundDistribution
from domain.funds.values import FundReserveType
from domain.protocol import SQLAlchemyRepositoryProtocol


class FundRepositoryProtocol(SQLAlchemyRepositoryProtocol[Fund], Protocol):

    async def get_last_opened(self, user_id: str) -> Optional[Fund]: ...

    async def get_last_unopened(self, user_id: str) -> Optional[Fund]: ...

    async def get_unopened(self, user_id: str, *specs) -> list[Fund]: ...

    async def get_count_by_user_id(self, user_id: str) -> int: ...


class FundDistRepositoryProtocol(
    SQLAlchemyRepositoryProtocol[FundDistribution], Protocol
):

    async def save_all(
        self, fund_dists: list[FundDistribution], commit: bool
    ) -> None: ...

    async def update_reserve_with_accumulate(
        self,
        reserve_type: FundReserveType,
        user_id: str,
        reserve_id: str,
        balance: Decimal,
    ) -> None: ...
