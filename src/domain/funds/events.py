from dataclasses import dataclass

from core.domain import DomainEvent


@dataclass(kw_only=True, frozen=True)
class FundClosedEvent(DomainEvent):
    """Накопительный остаток зафиксирован"""

    user_id: str
    fund_id: str
