from typing import Protocol, Optional

from users.values import UserId
from .domain import Account, AccountId


class AccountRepositoryProtocol(Protocol):

    async def save(self, account: Account) -> AccountId:
        pass

    async def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        pass

    async def delete(self, account_id: AccountId) -> None:
        pass

    async def count_by_user_id(self, user_id: UserId) -> int:
        pass

    async def is_name_taken(self, user_id: UserId, name: str) -> bool:
        pass
