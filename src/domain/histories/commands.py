from dataclasses import dataclass

from domain.histories.values import HistoryInterval


@dataclass(frozen=True)
class SaveHistoryCommand:
    user_id: str
    account_id: str
    balance: float
    delta: float


@dataclass(frozen=True)
class GetAccountHistoryCommand:
    user_id: str
    account_id: str
    interval: HistoryInterval
