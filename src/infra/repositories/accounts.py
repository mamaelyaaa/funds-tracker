from functools import lru_cache
from typing import Optional, Annotated

from fastapi import Depends

from accounts.domain import AccountId, Account
from accounts.repository import AccountRepositoryProtocol


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


@lru_cache
def get_account_repository() -> AccountRepositoryProtocol:
    return InMemoryAccountRepository()


AccountRepositoryDep = Annotated[
    AccountRepositoryProtocol, Depends(get_account_repository)
]
