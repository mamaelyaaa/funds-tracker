from functools import lru_cache
from typing import Optional, Annotated

from fastapi import Depends

from accounts.domain import AccountId, Account
from accounts.repository import AccountRepositoryProtocol
from users.values import UserId


class InMemoryAccountRepository:

    def __init__(self):
        self._storage: dict[AccountId, Account] = {}

    async def save(self, account: Account) -> AccountId:
        self._storage[account.id] = account
        return account.id

    async def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        return self._storage.get(account_id, None)

    async def delete(self, account_id: AccountId) -> None:
        self._storage.pop(account_id)

    async def count_by_user_id(self, user_id: UserId) -> int:
        return sum(1 for acc in self._storage.values() if acc.user_id == user_id)

    async def is_name_taken(self, user_id: UserId, name: str) -> bool:
        return any(
            acc.name == name and acc.user_id == user_id
            for acc in self._storage.values()
        )


@lru_cache
def get_account_repository() -> AccountRepositoryProtocol:
    return InMemoryAccountRepository()


AccountRepositoryDep = Annotated[
    AccountRepositoryProtocol, Depends(get_account_repository)
]
