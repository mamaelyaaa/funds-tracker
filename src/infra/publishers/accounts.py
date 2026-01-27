from typing import Annotated

from fastapi import Depends

from accounts.domain import BalanceUpdatedEvent
from accounts.publisher import AccountEventPublisherProtocol
from infra.tasks.accounts import sync_net_worth


class AccountTaskiqBroker:

    @staticmethod
    async def publish_balance_changed(event: BalanceUpdatedEvent) -> None:
        await sync_net_worth.kiq(event=event)
        return


def get_account_event_publisher() -> AccountEventPublisherProtocol:
    return AccountTaskiqBroker()


AccountEventPublisherDep = Annotated[
    AccountEventPublisherProtocol, Depends(get_account_event_publisher)
]
