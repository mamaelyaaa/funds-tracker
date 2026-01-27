from typing import Protocol, Optional

from .domain import Account, AccountId


class AccountRepositoryProtocol(Protocol):

    async def save(self, account: Account) -> AccountId:
        pass

    async def get_by_id(self, account_id: AccountId) -> Optional[Account]:
        pass
