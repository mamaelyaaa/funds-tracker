from pydantic import BaseModel


class BaseResponseSchema(BaseModel):
    message: str


class BaseResponseDetailSchema[D, M](BaseResponseSchema):
    detail: D
    metadata: M = {}


class BaseExceptionSchema(BaseResponseSchema):
    suggestion: str
