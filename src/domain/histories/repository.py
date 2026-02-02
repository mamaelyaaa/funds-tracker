from typing import Protocol, Optional

from domain.accounts.values import AccountId
from domain.histories.domain import AccountHistory
from domain.histories.values import SavingsId


class HistoryRepositoryProtocol(Protocol):

    async def save(self, savings: AccountHistory) -> SavingsId:
        pass

    async def get_by_id(self, savings_id: SavingsId) -> Optional[AccountHistory]:
        pass

    async def get_by_acc_id(
        self,
        account_id: AccountId,
        order_by: str = "id",
        asc: bool = True,
        limit: int = 10,
        offset: int = 0,
    ) -> list[AccountHistory]:
        pass
