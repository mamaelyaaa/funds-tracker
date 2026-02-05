import logging

import taskiq_fastapi
from taskiq import InMemoryBroker, AsyncBroker, SmartRetryMiddleware
from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from core.settings import settings

logger = logging.getLogger(__name__)


def setup_broker() -> AsyncBroker:
    if settings.app.env == "TEST":
        return InMemoryBroker()

    return (
        AioPikaBroker(url=settings.broker.AMQP_DSN)
        .with_result_backend(
            RedisAsyncResultBackend(
                redis_url=settings.cache.REDIS_DSN, result_ex_time=100
            )
        )
        .with_middlewares(
            SmartRetryMiddleware(
                default_retry_count=5,
                default_delay=10,
                use_jitter=True,
                use_delay_exponent=True,
                max_delay_exponent=120,
            )
        )
    )


broker = setup_broker()

taskiq_fastapi.init(broker, app_or_path="main:app")
