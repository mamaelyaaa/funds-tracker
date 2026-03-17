from datetime import datetime
from typing import Protocol, Optional

from domain.histories.entities import History
from domain.protocol import SQLAlchemyRepositoryProtocol


class HistoryRepositoryProtocol(SQLAlchemyRepositoryProtocol[History], Protocol):

    async def get_first_history_date_by_user(self, user_id: str) -> Optional[datetime]:
        pass

    async def get_sum_delta_in_period(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> int:
        pass
