from typing import Protocol, Optional

from users.values import UserId
from .domain import Account, AccountId
from .values import Title


class AccountRepositoryProtocol(Protocol):

    async def save(self, account: Account) -> AccountId:
        pass

    async def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        pass

    async def get_by_user_id(self, user_id: UserId) -> list[Account]:
        pass

    async def delete(self, account_id: AccountId) -> None:
        pass

    async def count_by_user_id(self, user_id: UserId) -> int:
        pass

    async def is_name_taken(self, user_id: UserId, name: Title) -> bool:
        pass

    async def update(self, account_id: AccountId, new_account: Account) -> None:
        pass
