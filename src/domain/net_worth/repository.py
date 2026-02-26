from datetime import datetime
from typing import Protocol


class NetWorthRepositoryProtocol(Protocol):

    async def get_user_total_balance(self, user_id: str) -> float:
        pass

    async def get_user_incomes(
        self,
        user_id: str,
        # period: str,
        # start_date: datetime,
    ) -> float:
        pass

    async def get_user_expenses(
        self,
        user_id: str,
        # period: str,
        # start_date: datetime,
    ) -> float:
        pass
