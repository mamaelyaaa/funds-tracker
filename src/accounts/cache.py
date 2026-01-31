from datetime import timedelta
from typing import Protocol, Optional

from accounts.entities import Account
from accounts.values import AccountId


class AccountCacheProtocol(Protocol):

    async def get(self, account_id: AccountId) -> Optional[Account]:
        pass

    async def set(
        self, account: Account, ttl: Optional[timedelta | int] = None
    ) -> None:
        pass
