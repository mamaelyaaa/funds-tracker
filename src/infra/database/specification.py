from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, Literal

from sqlalchemy import Select, desc, select, func, and_

from domain.commands import PaginationCommand
from infra.models import Base


class SpecificationProtocol(Protocol):
    """Протокол спецификации запроса в БД"""

    def apply(self, query: Select) -> Select: ...


@dataclass
class PaginationSpecification:
    """Спецификация на пагинацию запроса"""

    limit: int
    offset: int

    @classmethod
    def from_pagination_command(cls, command: PaginationCommand):
        return cls(limit=command.limit, offset=command.page_offset)

    def apply(self, query: Select) -> Select:
        return query.limit(self.limit).offset(self.offset)


@dataclass
class DateRangeSpecification:
    """Спецификация на фильтрацию по датам"""

    model: type[Base]
    field: str = field(default="created_at")
    start: datetime = None
    end: datetime = None

    def apply(self, query: Select) -> Select:
        column = getattr(self.model, self.field)
        conditions = []
        if self.start:
            conditions.append(column >= self.start)
        if self.end:
            conditions.append(column <= self.end)

        query = query.where(and_(*conditions))
        return query


@dataclass
class OrderBySpecification:
    field: str
    direction: Literal["asc", "desc"]

    def apply(self, query: Select) -> Select:
        return query.order_by(
            desc(self.field) if self.direction == "desc" else self.field
        )


@dataclass
class TimeTruncSpecification:
    model: type[Base]
    period: str

    def apply(self, query: Select) -> Select:
        if not hasattr(self.model, "created_at"):
            raise ValueError(
                "У модели нет столбца created_at для TimeTruncate спецификации"
            )

        subq = (
            select(
                func.max(self.model.created_at).label("last_date"),
                func.date_trunc(self.period, self.model.created_at).label("trunc_date"),
            )
            .group_by("trunc_date")
            .order_by(desc("trunc_date"))
            .subquery()
        )
        return query.join(subq, self.model.created_at == subq.c.last_date)
