from datetime import timedelta
from typing import Protocol, Optional

from domain.protocol import SQLAlchemyRepositoryProtocol, EventPublisherProtocol
from .entities import Account, AccountId


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


class AccountCacheProtocol(Protocol):

    async def get(self, account_id: AccountId) -> Optional[Account]:
        pass

    async def set(
        self, account: Account, ttl: Optional[timedelta | int] = None
    ) -> None:
        pass

    @staticmethod
    def account_key(account_id: AccountId) -> str:
        pass
