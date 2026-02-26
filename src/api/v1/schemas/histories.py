from datetime import datetime

from api.schemas import BaseApiModel
from domain.histories.values import HistoryInterval


class GetHistorySchema(BaseApiModel):
    interval: HistoryInterval


class HistoryDetailSchema(BaseApiModel):
    # id: str
    balance: float
    created_at: datetime


class HistoryMetadata(BaseApiModel):
    start_date: datetime
    period: str


class HistoryProfitSchema(BaseApiModel):
    percent_profit: float
    amount_profit: float
