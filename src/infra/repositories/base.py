from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from infra.repositories.dto.base import BaseOrmDTO


class BaseInMemoryRepository[Key, Type]:

    def __init__(self):
        self._storage: dict[Key, Type] = {}

    def clear(self) -> None:
        self._storage.clear()


class SQLAlchemyBaseRepository[Model, Entity]:

    def __init__(self, session: AsyncSession):
        self._session = session
        self._model: Model = None
        self._orm_dto: Optional[type[BaseOrmDTO[Model, Entity]]] = None

    async def save(self, entity: Entity) -> str:
        model: Model = self._orm_dto.from_entity_to_orm(entity)
        self._session.add(model)
        await self._session.commit()
        return model.id
