import uuid
from dataclasses import dataclass, field
from datetime import datetime


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
class DomainEntity:
    created_at: datetime = field(default_factory=datetime.now)
