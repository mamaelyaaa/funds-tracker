import asyncio
import logging
from typing import Annotated

from fastapi import Depends
from taskiq import TaskiqResult, AsyncTaskiqTask

from accounts.events import BalanceUpdatedEvent
from accounts.publisher import AccountEventPublisherProtocol
from core.domain import DomainEvent
from infra.tasks.accounts import sync_net_worth, make_account_screenshot

logger = logging.getLogger(__name__)


class AccountTaskiqPublisher:

    async def publish(self, event: DomainEvent) -> None:
        if isinstance(event, BalanceUpdatedEvent):
            task: AsyncTaskiqTask[str] = await sync_net_worth.kiq(event)
            logger.info(f"Синхронизируем капитал пользователя: task#{task.task_id}")
            asyncio.create_task(self._track_task_result(task))

            task: AsyncTaskiqTask[None] = await make_account_screenshot.kiq(event)
            logger.info(f"Обновляем историю счёта: task#{task.task_id}")
        return

    async def _track_task_result(self, task: AsyncTaskiqTask):
        """Фоновая задача для отслеживания результата"""
        # Ждем до 30 секунд
        result = await task.wait_result(timeout=30)
        logger.info(f"Задача {task.task_id} выполнена: {result.return_value}")


def get_account_event_publisher() -> AccountEventPublisherProtocol:
    return AccountTaskiqPublisher()


AccountEventPublisherDep = Annotated[
    AccountEventPublisherProtocol, Depends(get_account_event_publisher)
]
