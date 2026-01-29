import taskiq_fastapi
from taskiq import InMemoryBroker
from taskiq_aio_pika import AioPikaBroker

from core.settings import settings

if settings.app.env == "DEV":
    broker = AioPikaBroker(url=settings.broker.AMQP_DSN)
else:
    broker = InMemoryBroker()

taskiq_fastapi.init(broker, app_or_path="main:app")
