import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


class DomainValueObject[T](ABC):
    """Интерфейс для всех VO"""

    value: T


class DomainId(str, DomainValueObject[str]):
    """Базовый VO для ID"""

    def __new__(cls, value: Optional[str] = None):
        val = value or str(uuid.uuid4())
        return super().__new__(cls, val)

    @property
    def short(self) -> str:
        return self[:8]


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
