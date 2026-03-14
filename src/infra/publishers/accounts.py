import logging

from taskiq import AsyncTaskiqTask

from domain.accounts.events import (
    AccountCreatedEvent,
    BalanceUpdatedEvent,
)
from infra.tasks.accounts import save_account_history, create_or_update_user_fund_task
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

        history_task: AsyncTaskiqTask[str] = await save_account_history.kiq(event)
        history_id = await history_task.wait_result(timeout=5)
        logger.info(
            f"Результат задачи #{history_task.task_id} получен: {history_id.return_value}"
        )
        await create_or_update_user_fund_task.kiq(
            user_id=event.user_id,
            account_id=event.account_id,
            end_date=event.occurred_at,
        )
        return
