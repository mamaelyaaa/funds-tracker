import structlog
from taskiq import AsyncTaskiqTask

from domain.accounts.events import (
    AccountCreatedEvent,
    BalanceUpdatedEvent,
)
from domain.funds.values import FundId
from domain.histories.values import HistoryId
from infra.tasks.accounts import save_account_history, create_or_update_user_fund_task
from .base import BaseTaskiqPublisher

logger = structlog.get_logger()


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
            "История успешно создана",
            history_id=HistoryId(history_id.return_value).short,
        )

        if isinstance(event, AccountCreatedEvent) or (
            isinstance(event, BalanceUpdatedEvent) and event.is_monthly_closing
        ):
            fund_task: AsyncTaskiqTask[str] = await create_or_update_user_fund_task.kiq(
                user_id=event.user_id,
                account_id=event.account_id,
                end_date=event.occurred_at,
            )
            fund_id = await fund_task.wait_result(timeout=5)
            logger.info(
                "Остаток успешно обновлен",
                fund_id=FundId(fund_id.return_value).short,
            )

        return
