from typing import Optional, Any

from sqlalchemy import Select, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from infra.database.specification import SpecificationProtocol
from infra.models import Base
from infra.repositories.dto.base import BaseOrmDTO


class SQLAlchemyBaseRepository[Model: type[Base], Entity]:
    """Базовый SQLA репозиторий с реализациями"""

    model: Model
    dto: type[BaseOrmDTO]

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _apply_specs(query: Select, specs: tuple[SpecificationProtocol, ...]) -> Select:
        """Применяет спецификации к запросу, в котором есть *specs"""

        for spec in specs:
            query = spec.apply(query)
        return query

    async def save(self, entity: Entity, commit: bool = True) -> str:
        """Сохраняет запись в БД"""

        model = self.dto.from_entity_to_orm(entity)
        self.session.add(model)

        if commit:
            await self.session.commit()

        return model.id

    async def find_one(self, *specs, **filter_by) -> Optional[Entity]:
        """Находит строго одну запись в БД"""

        query = select(self.model).filter_by(**filter_by)
        query = self._apply_specs(query, specs)

        model = await self.session.scalar(query)
        return self.dto.from_orm_to_entity(model) if model else None

    async def find_all(self, *specs, **filter_by) -> list[Entity]:
        """Находит список записей в БД"""

        query = select(self.model).filter_by(**filter_by)
        query = self._apply_specs(query, specs)

        models = await self.session.scalars(query)
        return [self.dto.from_orm_to_entity(model) for model in models.all()]

    async def update(
        self,
        upd_data: dict[str, Any],
        commit: bool = True,
        *args,
        **filter_by,
    ) -> Optional[Entity]:
        """Обновляет запись в БД"""

        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**upd_data)
            .returning(self.model)
        )
        model = await self.session.scalar(stmt)
        if commit:
            await self.session.commit()

        return self.dto.from_orm_to_entity(model) if model else None

    async def delete_one(
        self, commit: bool = True, *args, **filter_by
    ) -> Optional[str]:
        """Удаляет одну запись из БД"""

        stmt = delete(self.model).filter_by(**filter_by).returning(self.model.id)
        id = await self.session.scalar(stmt)
        if commit:
            await self.session.commit()
        return id

    async def delete_all(self, commit: bool = True, *args, **filter_by) -> None:
        """Удаляет несколько записей из БД"""

        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)
        if commit:
            await self.session.commit()
        return
