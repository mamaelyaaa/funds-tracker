from datetime import datetime, timedelta
from typing import Protocol, Optional, Any

from domain.histories.entities import History


class HistoryRepositoryProtocol(Protocol):

    async def save(self, history: History) -> str:
        pass

    async def get_by_id(self, history_id: str) -> Optional[History]:
        pass

    async def get_history_linked_to_period(
        self,
        account_id: str,
        period: str,
        start_date: datetime,
        limit: Optional[int] = None,
        asc: bool = True,
    ) -> list[History]:
        pass

    async def update(
        self, history_id: str, upd_data: dict[str, Any]
    ) -> Optional[History]:
        pass

    async def get_acc_by_acc_id_with_time_limit(
        self, account_id: str, time_limit: timedelta
    ) -> Optional[History]:
        pass
