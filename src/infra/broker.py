import logging

import taskiq_fastapi
from taskiq import InMemoryBroker, AsyncBroker
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from core.settings import settings

logger = logging.getLogger(__name__)


def setup_broker() -> AsyncBroker:
    if settings.app.env == "TEST":
        return InMemoryBroker()

    return AioPikaBroker(url=settings.broker.AMQP_DSN).with_result_backend(
        RedisAsyncResultBackend(redis_url=settings.cache.REDIS_DSN, result_ex_time=1000)
    )


broker = setup_broker()

taskiq_fastapi.init(broker, app_or_path="main:app")
