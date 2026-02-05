from datetime import datetime, timedelta
from typing import Protocol, Optional

from domain.accounts.values import AccountId
from domain.histories.domain import History
from domain.histories.values import HistoryId


class HistoryRepositoryProtocol(Protocol):

    async def save(self, history: History) -> HistoryId:
        pass

    async def get_by_id(self, history_id: HistoryId) -> Optional[History]:
        pass

    async def get_history_linked_to_period(
        self, account_id: AccountId, period: str, start_date: datetime
    ) -> list[History]:
        pass

    async def update(self, history_id: HistoryId, new_history: History) -> History:
        pass

    async def get_acc_by_acc_id_with_time_limit(
        self, account_id: AccountId, time_limit: timedelta
    ) -> Optional[History]:
        pass
