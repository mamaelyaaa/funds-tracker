import asyncio
from typing import Callable

import structlog
from taskiq import AsyncTaskiqTask

from core.domain import DomainEvent

logger = structlog.get_logger()


class BaseTaskiqPublisher:
    """Базовый класс отправителя Taskiq"""

    handlers: dict[type[DomainEvent], list[Callable]]

    async def publish(self, event: DomainEvent) -> None:
        tasks = []
        for handler in self.handlers.get(type(event)):
            task = await handler(event)
            if task:
                tasks.append(task)
        if tasks:
            await self.track_tasks(tasks)

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
