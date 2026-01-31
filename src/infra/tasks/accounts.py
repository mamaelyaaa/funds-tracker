import logging
from typing import Annotated

from taskiq import TaskiqDepends

from accounts.events import BalanceUpdatedEvent
from infra import broker
from savings.service import SavingsHistoryService, get_savings_service

logger = logging.getLogger(__name__)


@broker.task
async def sync_net_worth(event: BalanceUpdatedEvent) -> str:
    logger.info(f"Синхронизируем капитал пользователя @{event.user_id.short}")
    logger.info(
        f"Динамика счёта: {event.old_balance} -> {event.new_balance} ({event.delta} {event.currency.value})"
    )
    return event.account_id.short


@broker.task
async def make_account_screenshot(
    event: BalanceUpdatedEvent,
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
