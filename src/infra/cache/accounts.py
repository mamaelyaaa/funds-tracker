import json
from datetime import timedelta, datetime
from typing import Optional, Annotated, Any

from fastapi import Depends
from redis.asyncio import Redis

from accounts.cache import AccountCacheProtocol
from accounts.entities import Account
from accounts.values import AccountId
from infra.cache.redis import RedisDep


class InMemoryAccountCache:

    def __init__(self):
        self._cache: dict[AccountId, Account] = {}

    async def get(self, account_id: AccountId) -> Optional[Account]:
        return self._cache.get(account_id, None)

    async def set(
        self, account: Account, ttl: Optional[timedelta | int] = None
    ) -> None:
        self._cache[account.id] = account
        return


class RedisAccountCache:

    def __init__(self, redis: Redis, default_ttl: int = 300):
        self._redis = redis
        self._default_ttl = default_ttl

    async def get(self, account_id: AccountId) -> Optional[Account]:
        account = await self._redis.get(self.account_key(account_id))
        if not account:
            return None
        data = json.loads(account)
        return self.deserialize(data)

    async def set(
        self, account: Account, ttl: Optional[timedelta | int] = None
    ) -> None:
        await self._redis.set(
            name=self.account_key(account.id),
            value=json.dumps(account.to_dict(all_str=True)),
            ex=ttl or self._default_ttl,
        )

    @staticmethod
    def account_key(account_id: AccountId) -> str:
        return f"account:{account_id.short}"

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Account:
        from users.values import UserId
        from accounts.values import Title

        return Account(
            id=AccountId(data.get("id")),
            user_id=UserId(data.get("id")),
            name=Title(data.get("name")),
            type=data.get("type"),
            currency=data.get("currency"),
            balance=data.get("balance"),
            created_at=datetime.fromisoformat(data.get("created_at")),
        )


def get_account_cache(redis: RedisDep) -> AccountCacheProtocol:
    return RedisAccountCache(redis)


AccountCacheDep = Annotated[AccountCacheProtocol, Depends(get_account_cache)]
