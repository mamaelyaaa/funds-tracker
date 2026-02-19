import asyncio
import logging
from typing import Callable, Annotated

from fastapi import Depends
from taskiq import AsyncTaskiqTask

from core.domain import DomainEvent
from domain.goals.events import GoalLinkedToAccountEvent
from domain.goals.protocols import GoalsEventPublisherProtocol
from infra.tasks.goals import goal_linked_to_account

logger = logging.getLogger(__name__)


class GoalsTaskiqPublisher:

    def __init__(self):
        self.handlers: dict[type[DomainEvent], list[Callable]] = {
            GoalLinkedToAccountEvent: [self._handle_goal_linked_to_account],
        }

    async def publish(self, event: DomainEvent) -> None:
        for handler in self.handlers.get(type(event)):
            await handler(event)
        return

    async def _handle_goal_linked_to_account(
        self, event: GoalLinkedToAccountEvent
    ) -> None:
        task = await goal_linked_to_account.kiq(event=event)
        await self.track_tasks([task])
        return

    @staticmethod
    async def track_tasks(tasks: list[AsyncTaskiqTask]) -> None:
        """Фоновая задача для отслеживания результатов"""

        for task in tasks:
            try:
                result = await task.wait_result(timeout=300)
                logger.info(
                    f"Задача #{task.task_id} выполнена: {result.returnas_generic_type()}"
                )

            except asyncio.TimeoutError:
                logger.warning(f"Задача #{task.task_id} не завершилась за 300 секунд")

            except Exception as e:
                logger.error(f"Ошибка в задаче #{task.task_id}: {e}")


def get_goals_event_publisher() -> GoalsEventPublisherProtocol:
    return GoalsTaskiqPublisher()


GoalsPublisherDep = Annotated[
    GoalsEventPublisherProtocol, Depends(get_goals_event_publisher)
]
