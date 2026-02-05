from dataclasses import dataclass

from domain.histories.values import HistoryInterval


@dataclass(frozen=True)
class SaveHistoryCommand:
    account_id: str
    balance: float


@dataclass(frozen=True)
class GetAccountHistoryCommand:
    account_id: str
    interval: HistoryInterval
