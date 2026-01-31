import uuid
from dataclasses import dataclass

from core.domain import DomainValueObject


@dataclass(frozen=True)
class SavingsId(DomainValueObject[str]):

    @classmethod
    def generate(cls) -> "SavingsId":
        return cls(value=str(uuid.uuid4()))
