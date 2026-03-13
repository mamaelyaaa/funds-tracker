from dataclasses import dataclass
from datetime import datetime

from domain.histories.values import HistoryInterval


@dataclass(frozen=True)
class SaveHistoryCommand:
    user_id: str
    account_id: str
    balance: float
    is_monthly_closing: bool
    created_at: datetime


@dataclass(frozen=True)
class GetAccountHistoryCommand:
    user_id: str
    account_id: str
    interval: HistoryInterval
