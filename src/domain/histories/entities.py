from dataclasses import dataclass, field

from core.domain import CreatedAtDomainMixin
from domain.accounts.values import AccountId
from domain.values import Money
from .values import HistoryId


@dataclass(kw_only=True)
class History(CreatedAtDomainMixin):
    """Доменная модель истории счёта"""

    id: HistoryId = field(default_factory=HistoryId.generate)
    account_id: AccountId
    balance: Money
    delta: float
    is_monthly_closing: bool
