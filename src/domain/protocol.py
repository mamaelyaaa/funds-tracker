from typing import Protocol, Optional, Any

from core.domain import DomainEvent


class SQLAlchemyRepositoryProtocol[E](Protocol):
    """Протокол SQLAlchemy репозитория"""

    async def save(self, model: E, commit: bool = True) -> str: ...

    async def find_one(self, *specs, **filter_by) -> Optional[E]: ...

    async def find_all(self, *specs, **filter_by) -> list[E]: ...

    async def update(
        self, upd_data: dict[str, Any], commit: bool = True, *args, **filter_by
    ) -> Optional[E]: ...

    async def delete_one(
        self, commit: bool = True, *args, **filter_by
    ) -> Optional[str]: ...


class EventPublisherProtocol(Protocol):
    """Протокол паблишера событий"""

    async def publish(self, event: DomainEvent) -> None: ...
