import uuid
from datetime import datetime

from api.schemas import BaseApiModel
from domain.funds.values import FundStatus, FundReserveType


class FundDetailSchema(BaseApiModel):
    id: uuid.UUID
    total_amount: float
    status: FundStatus
    start_date: datetime
    end_date: datetime
    created_at: datetime


class ReserveSchema(BaseApiModel):
    reserve_id: uuid.UUID
    reserve_type: FundReserveType
    percent: int


class FundCloseSchema(BaseApiModel):
    reserves: list[ReserveSchema]
