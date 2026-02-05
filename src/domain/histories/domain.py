from dataclasses import dataclass, field
from datetime import datetime

from domain.accounts.exceptions import InvalidInitBalanceException
from domain.accounts.values import AccountId
from .values import HistoryId


@dataclass
class History:
    account_id: AccountId
    balance: float
    id: HistoryId = field(default_factory=HistoryId.generate)
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, account_id: AccountId, balance: float) -> "History":
        if balance < 0:
            raise InvalidInitBalanceException
        return cls(balance=balance, account_id=account_id)
