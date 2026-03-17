from typing import Protocol

from domain.protocol import SQLAlchemyRepositoryProtocol, EventPublisherProtocol
from .entity import Account


class AccountRepositoryProtocol(SQLAlchemyRepositoryProtocol[Account], Protocol):
    """Протокол репозитория для работы со счетом"""

    async def count_by_user_id(self, user_id: str) -> int:
        pass

    async def is_name_taken(self, user_id: str, name: str) -> bool:
        pass

    async def check_exists_by_id(self, user_id: str, account_id: str) -> bool: ...


class AccountEventPublisherProtocol(EventPublisherProtocol, Protocol):
    """Протокол паблишера для работы со счетом"""

    pass
