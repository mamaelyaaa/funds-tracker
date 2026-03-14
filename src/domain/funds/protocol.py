from decimal import Decimal
from typing import Protocol, Any, Optional

from core.domain import DomainEvent
from domain.funds.entity import Fund, FundDistribution
from domain.funds.values import FundReserveType


class FundRepositoryProtocol(Protocol):

    async def save(self, fund: Fund) -> str: ...

    async def update(
        self,
        user_id: str,
        fund_id: str,
        upd_data: dict[str, Any],
        commit: bool = True,
    ) -> Optional[Fund]: ...

    async def get_by_user_id(
        self, user_id: str, *args, **filter_by
    ) -> Optional[Fund]: ...

    async def get_by_id(self, fund_id: str) -> Optional[Fund]: ...

    async def get_last_opened(self, user_id: str) -> Optional[Fund]: ...

    async def get_last_closed(self, user_id: str) -> Optional[Fund]: ...

    async def get_unopened(self, user_id: str) -> list[Fund]: ...


class FundDistRepositoryProtocol(Protocol):

    async def save_all(
        self, fund_dists: list[FundDistribution], commit: bool
    ) -> None: ...

    async def get_by_find_id(self, fund_id: str) -> list[FundDistribution]: ...

    async def update_reserve_with_accumulate(
        self,
        reserve_type: FundReserveType,
        user_id: str,
        reserve_id: str,
        balance: Decimal,
    ) -> None: ...


class FundDistPublisherProtocol(Protocol):

    async def publish(self, event: DomainEvent) -> None:
        pass
