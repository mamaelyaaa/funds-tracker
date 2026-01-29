import logging

from accounts.domain import BalanceUpdatedEvent
from infra import broker

logger = logging.getLogger(__name__)


@broker.task
async def sync_net_worth(event: BalanceUpdatedEvent) -> str:
    logger.info(f"Синхронизируем капитал пользователя @{event.user_id.short}")
    logger.info(
        f"Динамика счёта: {event.old_balance} -> {event.new_balance} ({event.delta} {event.currency.value})"
    )
    return event.account_id.short
