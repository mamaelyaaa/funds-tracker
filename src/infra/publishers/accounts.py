import asyncio
import logging
from typing import Annotated, Callable

from fastapi import Depends
from taskiq import AsyncTaskiqTask

from core.domain import DomainEvent
from domain.accounts.events import AccountCreatedEvent, BalanceUpdatedEvent
from domain.accounts.publisher import AccountEventPublisherProtocol
from infra.tasks.accounts import save_account_history

logger = logging.getLogger(__name__)


class AccountTaskiqPublisher:

    def __init__(self):
        self.handlers: dict[type[DomainEvent], list[Callable]] = {
            AccountCreatedEvent: [self._handle_account_update_history],
            BalanceUpdatedEvent: [self._handle_account_update_history],
        }

    async def publish(self, event: DomainEvent) -> None:
        for handler in self.handlers.get(type(event)):
            await handler(event)
        return

    async def _handle_account_update_history(self, event: AccountCreatedEvent) -> None:
        task: AsyncTaskiqTask = await save_account_history.kiq(event)
        logger.info(f"Обновляем историю счёта: task#{task.task_id}")
        asyncio.create_task(self.track_tasks([task]))
        return

    @staticmethod
    async def track_tasks(tasks: list[AsyncTaskiqTask]) -> None:
        """Фоновая задача для отслеживания результатов"""

        for task in tasks:
            try:
                result = await task.wait_result(timeout=300)
                logger.info(f"Задача #{task.task_id} выполнена: {result.return_value}")

            except asyncio.TimeoutError:
                logger.warning(f"Задача #{task.task_id} не завершилась за 300 секунд")

            except Exception as e:
                logger.error(f"Ошибка в задаче #{task.task_id}: {e}")


def get_account_event_publisher() -> AccountEventPublisherProtocol:
    return AccountTaskiqPublisher()


AccountEventPublisherDep = Annotated[
    AccountEventPublisherProtocol, Depends(get_account_event_publisher)
]
