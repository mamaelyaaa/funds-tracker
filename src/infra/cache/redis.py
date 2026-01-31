from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from core.settings import settings


@lru_cache
def get_redis_client() -> Redis:
    return Redis(host=settings.cache.host, port=settings.cache.port)


RedisDep = Annotated[Redis, Depends(get_redis_client)]
