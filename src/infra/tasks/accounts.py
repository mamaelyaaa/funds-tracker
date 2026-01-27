import logging

from accounts.domain import AccountId
from infra.broker import broker

logger = logging.getLogger(__name__)


@broker.task
async def sync_net_worth(account_id: AccountId) -> str:
    logger.info(f"Синхронизируем капитал пользователя #{account_id.short}")
    return account_id.short
