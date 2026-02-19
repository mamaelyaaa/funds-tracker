from dataclasses import dataclass, field

from core.domain import DomainEntity
from domain.accounts.exceptions import InvalidInitBalanceException
from domain.accounts.values import AccountId
from .values import HistoryId


@dataclass(kw_only=True)
class History(DomainEntity):
    """Доменная модель истории счёта"""

    id: HistoryId = field(default_factory=HistoryId.generate)
    account_id: AccountId
    balance: float

    @classmethod
    def create(cls, account_id: str, balance: float) -> "History":
        if balance < 0:
            raise InvalidInitBalanceException
        return cls(balance=balance, account_id=AccountId(account_id))
