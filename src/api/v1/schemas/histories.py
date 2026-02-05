from datetime import datetime

from pydantic import BaseModel

from domain.histories.commands import HistoryInterval
from domain.histories.domain import History


class GetHistorySchema(BaseModel):
    interval: HistoryInterval


class HistoryDetailSchema(BaseModel):
    # id: str
    balance: float
    created_at: datetime

    @classmethod
    def from_model(cls, history: History) -> "HistoryDetailSchema":
        return HistoryDetailSchema(
            # id=history.id.value,
            balance=history.balance,
            created_at=history.created_at,
        )
