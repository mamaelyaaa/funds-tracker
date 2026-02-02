import logging
from typing import Annotated

from taskiq import TaskiqDepends

from domain.accounts.events import AccountCreatedEvent
from domain.savings.service import SavingsHistoryService, get_savings_service
from infra import broker

logger = logging.getLogger(__name__)


@broker.task
async def save_account_history(
    event: AccountCreatedEvent,
    savings_service: Annotated[
        SavingsHistoryService, TaskiqDepends(get_savings_service)
    ],
) -> str:
    logger.info(f"Сохраняем историю счёта #{event.account_id.short} ...")
    savings_id: str = await savings_service.make_account_screenshot(
        balance=event.new_balance,
        account_id=event.account_id.value,
    )
    return savings_id
