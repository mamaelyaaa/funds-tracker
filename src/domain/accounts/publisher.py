from typing import Protocol

from core.domain import DomainEvent


class AccountEventPublisherProtocol(Protocol):

    async def publish(self, event: DomainEvent) -> None:
        pass
