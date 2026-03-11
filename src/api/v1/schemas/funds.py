from datetime import datetime

from api.schemas import BaseApiModel
from domain.funds.values import FundStatus


class FundDetailSchema(BaseApiModel):
    id: str
    user_id: str
    total_amount: float
    status: FundStatus
    start_date: datetime
    end_date: datetime
    created_at: datetime
