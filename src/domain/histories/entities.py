from dataclasses import dataclass, field

from core.mixins import CreatedAtDomainMixin
from domain.accounts.values import AccountId
from domain.values import Money
from .values import HistoryId


@dataclass(kw_only=True)
class History(CreatedAtDomainMixin):
    """Доменная модель истории счёта"""

    id: HistoryId = field(default_factory=HistoryId)
    account_id: AccountId
    balance: Money
    delta: float = field(default=0)
    is_monthly_closing: bool
