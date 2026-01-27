import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import router as main_router
from api.schemas import BaseExceptionSchema
from core.exceptions import AppException
from core.logger import setup_logger

setup_logger()

app = FastAPI()
app.include_router(main_router)


@app.exception_handler(AppException)
async def handle_app_exception(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseExceptionSchema(
            message=exc.message,
            suggestion=exc.suggestion,
        ).model_dump(exclude_none=True, exclude_unset=True),
    )


if __name__ == "__main__":
    uvicorn.run(app="src.main:app", reload=True)
