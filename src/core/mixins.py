from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.domain import DomainEvent


@dataclass
class DomainEventMixin:
    _events: list[DomainEvent] = field(default_factory=list)

    @property
    def events(self) -> list[DomainEvent]:
        return self._events


@dataclass
class CreatedAtDomainMixin:
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UpdatedAtDomainMixin:
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        """Обновление updated_at"""
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class TimestampDomainMixin(CreatedAtDomainMixin, UpdatedAtDomainMixin):
    pass
