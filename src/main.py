from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from api import router as main_router
from api.schemas import BaseExceptionSchema
from core.exceptions import AppException
from core.logger import setup_logger
from core.settings import settings
from infra.broker import broker

setup_logger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not broker.is_worker_process:
        await broker.startup()

    yield

    if not broker.is_worker_process:
        await broker.shutdown()


app = FastAPI(
    title=settings.app.title,
    debug=settings.app.debug,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

app.include_router(main_router)


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
    uvicorn.run(app="src.main:app", reload=True)
