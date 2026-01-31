import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api import router as main_router
from api.schemas import BaseExceptionSchema
from core.exceptions import AppException
from core.logger import setup_logger
from core.settings import settings
from infra.admin import admin
from infra.broker import broker
from infra.cache.redis import get_redis_client
from infra.database import db_helper

setup_logger()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI, redis: Redis = get_redis_client()):
    if not broker.is_worker_process:
        await broker.startup()

    yield

    if not broker.is_worker_process:
        await broker.shutdown()

    await db_helper.dispose()
    await redis.aclose()


app = FastAPI(
    title=settings.app.title,
    debug=settings.app.debug,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

app.include_router(main_router)
admin.mount_to(app)


@app.exception_handler(AppException)
async def handle_app_exception(request: Request, exc: AppException):
    return ORJSONResponse(
        status_code=exc.status_code,
        content=BaseExceptionSchema(
            message=exc.message,
            suggestion=exc.suggestion,
        ).model_dump(exclude_none=True, exclude_unset=True),
    )


if __name__ == "__main__":
    if settings.app.env == "TEST":
        logger.warning(
            "Запущено на тестовом окружении. Будет использован in-memory брокер"
        )

    uvicorn.run(app="src.main:app", reload=True)
