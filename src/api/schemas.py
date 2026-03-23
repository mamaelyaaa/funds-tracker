import math

import structlog
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)
from pydantic.alias_generators import to_camel

from domain.exceptions import UnknownPageException

logger = structlog.get_logger()


class BaseApiModel(BaseModel):
    """Базовая API схема"""

    model_config = ConfigDict(
        alias_generator=to_camel, validate_by_name=True, extra="ignore"
    )


class BaseResponseSchema(BaseApiModel):
    """Базовая схема ответа от API"""

    message: str


class BaseResponseDetailSchema[D, M](BaseResponseSchema):
    """Детальная схема ответа от API"""

    detail: D
    metadata: M


class BaseExceptionSchema(BaseResponseSchema):
    """Базовая схема ошибки от API"""

    suggestion: str


class ValidationDetailSchema(BaseApiModel):
    """Подробности ошибки валидации"""

    field: str
    message: str
    type: str


class ValidationExceptionSchema(BaseResponseSchema):
    """Схема ошибки валидации от API"""

    message: str = "Ошибка валидации входных данных"
    detail: list[ValidationDetailSchema]


class PaginationUseSchema(BaseApiModel):
    """Схема пагинации для запроса"""

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=5, ge=1, le=100)


class PaginationMetaSchema(PaginationUseSchema):
    """Схема мета информации о пагинации"""

    total_found: int

    @computed_field
    @property
    def total_pages(self) -> int:
        if self.total_found == 0:
            return 1
        return math.ceil(self.total_found / self.limit)

    @model_validator(mode="after")
    def unknown_page(self):
        if self.page > self.total_pages:
            logger.error("Страница не найдена")
            raise UnknownPageException
        return self
