import logging

from domain.accounts.events import (
    AccountCreatedEvent,
    BalanceUpdatedEvent,
)
from infra.tasks.accounts import save_account_history
from .base import BaseTaskiqPublisher

logger = logging.getLogger(__name__)


class AccountTaskiqPublisher(BaseTaskiqPublisher):

    def __init__(self):
        self.handlers = {
            AccountCreatedEvent: [self._handle_account_update_history],
            BalanceUpdatedEvent: [
                self._handle_account_update_history,
            ],
        }

    @staticmethod
    async def _handle_account_update_history(
        event: AccountCreatedEvent | BalanceUpdatedEvent,
    ) -> None:

        return await save_account_history.kiq(event)
