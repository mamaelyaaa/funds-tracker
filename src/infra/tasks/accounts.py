import logging
from typing import Annotated

from taskiq import TaskiqDepends

from domain.accounts.events import AccountCreatedEvent, BalanceUpdatedEvent
from domain.histories.commands import SaveHistoryCommand
from domain.histories.service import get_history_service, HistoryService
from infra import broker

logger = logging.getLogger(__name__)


@broker.task(retry_on_error=True, max_retries=10)
async def save_account_history(
    event: AccountCreatedEvent | BalanceUpdatedEvent,
    history_service: Annotated[HistoryService, TaskiqDepends(get_history_service)],
) -> str:
    logger.info(f"Сохраняем историю счёта #{event.account_id[:8]} ...")

    history_id: str = await history_service.save_account_history(
        command=SaveHistoryCommand(
            balance=event.new_balance,
            account_id=event.account_id,
            user_id=event.user_id,
            delta=event.delta if isinstance(event, BalanceUpdatedEvent) else 0,
        )
    )
    return history_id
