import uuid
from datetime import datetime

from api.schemas import BaseApiModel
from domain.funds.commands import ReserveCreateCommand
from domain.funds.values import FundStatus


class FundDetailSchema(BaseApiModel):
    id: uuid.UUID
    total_amount: float
    status: FundStatus
    start_date: datetime
    end_date: datetime
    created_at: datetime


class FundCloseSchema(BaseApiModel):
    reserves: list[ReserveCreateCommand]
