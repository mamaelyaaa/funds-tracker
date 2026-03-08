from typing import Protocol, Optional, Any

from core.domain import DomainEvent
from .entity import Account


class AccountRepositoryProtocol(Protocol):

    async def save(self, account: Account) -> str:
        pass

    async def get_by_id(self, user_id: str, account_id: str) -> Optional[Account]:
        pass

    async def get_by_user_id(self, user_id: str) -> list[Account]:
        pass

    async def delete(self, user_id: str, account_id: str) -> Optional[str]:
        pass

    async def count_by_user_id(self, user_id: str) -> int:
        pass

    async def is_name_taken(self, user_id: str, name: str) -> bool:
        pass

    async def update(
        self, user_id: str, account_id: str, upd_data: dict[str, Any]
    ) -> Optional[Account]:
        pass


class AccountEventPublisherProtocol(Protocol):

    async def publish(self, event: DomainEvent) -> None:
        pass
