from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from infra.database.specification import SpecificationProtocol


class SQLAlchemyBaseRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _apply_specs(query: Select, specs: tuple[SpecificationProtocol, ...]) -> Select:
        """Применяет спецификации к запросу, в котором есть *specs"""

        for spec in specs:
            query = spec.apply(query)
        return query
