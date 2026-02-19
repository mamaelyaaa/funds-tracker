from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class DomainValueObject[T](ABC):
    _value: T

    @abstractmethod
    def as_generic_type(self) -> T:
        pass


@dataclass
class DomainEntity:
    created_at: datetime = field(default_factory=datetime.now)
