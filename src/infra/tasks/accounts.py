import logging

from accounts.domain import BalanceUpdatedEvent
from infra.broker import broker

logger = logging.getLogger(__name__)


@broker.task
async def sync_net_worth(event: BalanceUpdatedEvent) -> str:
    logger.info(f"Синхронизируем капитал пользователя #{event.account_id.short}")
    return event.account_id.short
