from datetime import datetime

from api.schemas import BaseApiModel
from domain.histories.commands import HistoryInterval
from domain.histories.entities import History


class GetHistorySchema(BaseApiModel):
    interval: HistoryInterval


class HistoryDetailSchema(BaseApiModel):
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


class HistoryPercentChangeSchema(BaseApiModel):
    percent_profit: float
