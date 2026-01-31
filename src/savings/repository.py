from typing import Protocol, Optional

from savings.domain import SavingsHistory
from savings.values import SavingsId


class SavingsHistoryRepositoryProtocol(Protocol):

    async def save(self, savings: SavingsHistory) -> SavingsId:
        pass

    async def get_by_id(self, savings_id: SavingsId) -> Optional[SavingsHistory]:
        pass
