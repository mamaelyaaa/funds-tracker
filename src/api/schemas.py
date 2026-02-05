from pydantic import BaseModel


class BaseResponseSchema(BaseModel):
    message: str


class BaseResponseDetailSchema[D, M](BaseResponseSchema):
    detail: D
    metadata: M


class BaseExceptionSchema(BaseResponseSchema):
    suggestion: str


class ValidationDetailSchema(BaseModel):
    field: str
    message: str
    type: str


class ValidationExceptionSchema(BaseResponseSchema):
    message: str = "Ошибка валидации входных данных"
    detail: list[ValidationDetailSchema]


class PaginationSchema(BaseModel):
    page: int
    limit: int
