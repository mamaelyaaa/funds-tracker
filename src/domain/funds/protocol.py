from decimal import Decimal
from typing import Protocol, Optional

from domain.funds.entity import Fund, FundDistribution
from domain.funds.values import FundReserveType
from domain.protocol import SQLAlchemyRepositoryProtocol


class FundRepositoryProtocol(SQLAlchemyRepositoryProtocol[Fund], Protocol):
    """Протокол репозитория для работы с остатком"""

    async def get_last_opened(self, user_id: str) -> Optional[Fund]: ...

    async def get_last_unopened(self, user_id: str) -> Optional[Fund]: ...

    async def get_unopened(self, user_id: str, *specs) -> list[Fund]: ...

    async def get_count_by_user_id(self, user_id: str) -> int: ...


class FundDistRepositoryProtocol(
    SQLAlchemyRepositoryProtocol[FundDistribution], Protocol
):
    """Протокол репозитория для работы с распределением остатка"""

    async def save_all(
        self, fund_dists: list[FundDistribution], commit: bool
    ) -> None: ...
