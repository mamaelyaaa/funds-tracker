import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api import router as main_router
from api.schemas import (
    BaseExceptionSchema,
    ValidationExceptionSchema,
    ValidationDetailSchema,
)
from core.exceptions import AppException
from core.logger import setup_logger
from core.settings import settings
from infra import admin, broker, db_helper
from infra.cache.redis import get_redis_client

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
    responses={
        422: {
            "model": ValidationExceptionSchema,
            "description": "Ошибка валидации входных данных",
        }
    },
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors: list[ValidationDetailSchema] = []
    for error in exc.errors():
        errors.append(
            ValidationDetailSchema.model_validate(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
        )

    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ValidationExceptionSchema(
            message="Ошибка валидации данных",
            detail=errors,
        ).model_dump(exclude_none=True),
    )


if __name__ == "__main__":
    if settings.app.env == "TEST":
        logger.warning(
            "Запущено на тестовом окружении. Будет использован in-memory брокер"
        )

    uvicorn.run(app="src.main:app", reload=True)
