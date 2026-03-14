from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import Select

from domain.commands import PaginationCommand


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
