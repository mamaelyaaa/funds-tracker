import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class DomainValueObject[T]:
    _value: T

    def as_generic_type(self) -> T:
        return self._value


@dataclass(frozen=True)
class DomainIdValueObject(DomainValueObject[str]):

    @classmethod
    def generate(cls):
        return cls(_value=str(uuid.uuid4()))

    @property
    def short(self) -> str:
        return self._value[:8]


@dataclass
class CreatedAtDomainMixin:
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UpdatedAtDomainMixin:
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def _touch(self) -> None:
        """Обновление updated_at"""
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class TimestampDomainMixin(CreatedAtDomainMixin, UpdatedAtDomainMixin):
    pass


@dataclass
class EventDomainMixin:
    _events: list[DomainEvent] = field(default_factory=list)

    @property
    def events(self) -> list[DomainEvent]:
        return self._events
