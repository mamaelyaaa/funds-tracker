from pydantic import BaseModel


class BaseResponseSchema(BaseModel):
    message: str


class BaseResponseDetailSchema[T](BaseResponseSchema):
    detail: T


class BaseExceptionSchema(BaseResponseSchema):
    suggestion: str
