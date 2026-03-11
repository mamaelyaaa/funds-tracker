from typing import Protocol, Optional, Any

from core.domain import DomainEvent
from .entities import Goal


class GoalRepositoryProtocol(Protocol):

    async def save(self, goal: Goal) -> str: ...

    async def get_by_id(self, user_id: str, goal_id: str) -> Optional[Goal]: ...

    async def is_title_taken(self, title: str, user_id: str) -> bool: ...

    async def count(self) -> int: ...

    async def get_by_user_id(self, user_id: str) -> list[Goal]: ...

    async def get_by_user_id_except_goal_id(
        self, user_id: str, goal_id: str
    ) -> list[Goal]: ...

    async def delete(self, goal: Goal) -> None: ...

    async def update(
        self, user_id: str, goal_id: str, upd_data: dict[str, Any], commit: bool
    ) -> Optional[Goal]: ...

    async def check_exists_by_id(self, user_id: str, account_id: str) -> bool: ...


class GoalsEventPublisherProtocol(Protocol):

    async def publish(self, event: DomainEvent) -> None: ...
