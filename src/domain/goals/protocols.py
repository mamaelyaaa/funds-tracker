from typing import Protocol, Optional, Any

from core.domain import DomainEvent
from .entities import Goal


class GoalsRepositoryProtocol(Protocol):

    async def save(self, goal: Goal) -> None: ...

    async def get_by_id(self, goal_id: str) -> Optional[Goal]: ...

    async def is_title_taken(self, title: str, user_id: str) -> bool: ...

    async def count(self) -> int: ...

    async def get_by_user_id(self, user_id: str) -> list[Goal]: ...

    async def get_by_user_id_except_goal_id(
        self, user_id: str, goal_id: str
    ) -> list[Goal]: ...

    async def delete(self, goal: Goal) -> None: ...

    async def update(self, goal_id: str, new_goal: dict[str, Any]) -> Goal: ...


class GoalsEventPublisherProtocol(Protocol):

    async def publish(self, event: DomainEvent) -> None: ...
