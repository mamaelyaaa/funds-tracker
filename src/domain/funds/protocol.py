from typing import Protocol, Any, Optional

from domain.funds.entity import Fund


class FundRepositoryProtocol(Protocol):

    async def save(self, fund: Fund) -> str: ...

    async def update(
        self,
        user_id: str,
        fund_id: str,
        upd_data: dict[str, Any],
    ) -> Optional[Fund]: ...

    async def get_by_user_id(
        self, user_id: str, *args, **filter_by
    ) -> Optional[Fund]: ...

    async def get_last_opened(self, user_id: str) -> Optional[Fund]: ...

    async def get_last_closed(self, user_id: str) -> Optional[Fund]: ...


# class FundRuleRepositoryProtocol(Protocol):
#
#     async def save(self, funds_rules: FundRule) -> str: ...
#
#     async def get_by_user_and_reserve_id(
#         self, user_id: str, reserve_id: str
#     ) -> Optional[FundRule]: ...


class FundDistributionRepositoryProtocol(Protocol):
    pass
