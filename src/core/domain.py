from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class DomainValueObject[T]:
    value: T


@dataclass
class DomainEntity(ABC):
    created_at: datetime = field(default_factory=datetime.now)
    _events: list[DomainEvent] = field(default_factory=list)

    @abstractmethod
    def to_dict(self, all_str: bool = False) -> dict[str, Any]:
        pass

    @property
    def events(self) -> list[DomainEvent]:
        return self._events
