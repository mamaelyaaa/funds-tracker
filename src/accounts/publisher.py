from typing import Protocol

from accounts.domain import BalanceUpdatedEvent


class AccountEventPublisherProtocol(Protocol):

    async def publish_balance_changed(self, event: BalanceUpdatedEvent) -> None:
        pass
