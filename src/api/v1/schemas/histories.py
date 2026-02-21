from datetime import datetime

from api.schemas import BaseApiModel
from domain.histories.commands import HistoryInterval


class GetHistorySchema(BaseApiModel):
    interval: HistoryInterval


class HistoryDetailSchema(BaseApiModel):
    # id: str
    balance: float
    created_at: datetime


class HistoryPercentChangeSchema(BaseApiModel):
    percent_profit: float
