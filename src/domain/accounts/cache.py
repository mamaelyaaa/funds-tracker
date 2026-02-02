from datetime import timedelta
from typing import Protocol, Optional

from domain.accounts.entity import Account
from domain.accounts.values import AccountId


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
