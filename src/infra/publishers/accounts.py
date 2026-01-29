import logging
from typing import Annotated

from fastapi import Depends

from accounts.domain import BalanceUpdatedEvent
from accounts.publisher import AccountEventPublisherProtocol
from core.domain import DomainEvent
from infra.tasks.accounts import sync_net_worth

logger = logging.getLogger(__name__)


class AccountTaskiqBroker:

    async def publish(self, event: DomainEvent) -> None:
        if isinstance(event, BalanceUpdatedEvent):
            await sync_net_worth.kiq(event=event)
        return


def get_account_event_publisher() -> AccountEventPublisherProtocol:
    return AccountTaskiqBroker()


AccountEventPublisherDep = Annotated[
    AccountEventPublisherProtocol, Depends(get_account_event_publisher)
]
