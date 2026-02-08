from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
    )


class BaseResponseSchema(BaseApiModel):
    message: str


class BaseResponseDetailSchema[D, M](BaseResponseSchema):
    detail: D
    metadata: M


class BaseExceptionSchema(BaseResponseSchema):
    suggestion: str


class ValidationDetailSchema(BaseApiModel):
    field: str
    message: str
    type: str


class ValidationExceptionSchema(BaseResponseSchema):
    message: str = "Ошибка валидации входных данных"
    detail: list[ValidationDetailSchema]


class PaginationSchema(BaseApiModel):
    page: int
    limit: int
