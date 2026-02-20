from typing import Optional, Annotated, Any

from fastapi import Depends
from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.goals.entities import Goal
from domain.goals.protocols import GoalsRepositoryProtocol
from infra.database import SessionDep
from infra.models.goals import GoalModel
from .base import BaseInMemoryRepository
from .dto.goals import GoalDTO, GoalOrmDTO


class InMemoryGoalsRepository(BaseInMemoryRepository[str, Goal]):

    async def save(self, goal: Goal) -> str:
        self._storage[goal.id.as_generic_type()] = goal
        return goal.id.as_generic_type()

    async def get_by_id(self, user_id: str, goal_id: str) -> Optional[Goal]:
        goal = self._storage.get(goal_id, None)
        if not goal:
            return None
        return goal if goal.user_id.as_generic_type() == user_id else None

    async def is_title_taken(self, title: str, user_id: str) -> bool:
        return any(
            goal
            for goal in self._storage.values()
            if goal.title.as_generic_type() == title
            and goal.user_id.as_generic_type() == user_id
        )

    async def count(self) -> int:
        return len(self._storage)

    async def get_by_user_id(self, user_id: str) -> list[Goal]:
        return [
            goal
            for goal in self._storage.values()
            if goal.user_id.as_generic_type() == user_id
        ]

    async def get_by_user_id_except_goal_id(
        self, user_id: str, goal_id: str
    ) -> list[Goal]:
        return [
            goal
            for goal in self._storage.values()
            if goal.user_id.as_generic_type() == user_id
            and goal.id.as_generic_type() != goal_id
        ]

    async def delete(self, goal: Goal) -> None:
        self._storage.pop(goal.id.as_generic_type())

    async def update(
        self, user_id: str, goal_id: str, new_goal: dict[str, Any]
    ) -> Goal:
        exists_goal = await self.get_by_id(user_id=user_id, goal_id=goal_id)
        exists_goal_dict = GoalDTO.from_entity_to_dict(exists_goal)
        exists_goal_dict.update(**new_goal)
        return GoalDTO.from_dict_to_entity(exists_goal_dict)


class PostgresGoalsRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, goal: Goal) -> str:
        goal_model: GoalModel = GoalOrmDTO.from_entity_to_orm(goal)
        self._session.add(goal_model)
        await self._session.commit()
        return goal_model.id

    async def get_by_id(self, user_id: str, goal_id: str) -> Optional[Goal]:
        query = select(GoalModel).filter_by(id=goal_id, user_id=user_id)
        goal = await self._session.scalar(query)
        return GoalOrmDTO.from_orm_to_entity(goal) if goal else None

    async def is_title_taken(self, title: str, user_id: str) -> bool:
        query = (
            select(func.count())
            .select_from(GoalModel)
            .filter_by(title=title, user_id=user_id)
        )
        res = await self._session.execute(query)
        return bool(res.scalar_one())

    async def count(self) -> int:
        query = select(func.count()).select_from(GoalModel)
        res = await self._session.execute(query)
        return res.scalar_one()

    async def get_by_user_id(self, user_id: str) -> list[Goal]:
        query = select(GoalModel).filter_by(user_id=user_id)
        res = await self._session.execute(query)
        return [GoalOrmDTO.from_orm_to_entity(row) for row in res.scalars()]

    async def get_by_user_id_except_goal_id(
        self, user_id: str, goal_id: str
    ) -> list[Goal]:
        query = (
            select(GoalModel).filter_by(user_id=user_id).where(GoalModel.id != goal_id)
        )
        res = await self._session.execute(query)
        return [GoalOrmDTO.from_orm_to_entity(row) for row in res.scalars()]

    async def delete(self, goal: Goal) -> None:
        stmt = delete(GoalModel).where(
            user_id=goal.user_id.as_generic_type(),
            goal_id=goal.id.as_generic_type(),
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def update(
        self, user_id: str, goal_id: str, new_goal: dict[str, Any]
    ) -> Optional[Goal]:
        stmt = (
            update(GoalModel)
            .filter_by(id=goal_id, user_id=user_id)
            .values(**new_goal)
            .returning(GoalModel)
        )
        goal = await self._session.scalar(stmt)
        await self._session.commit()
        return GoalOrmDTO.from_orm_to_entity(goal) if goal else None


def get_goals_repository(session: SessionDep) -> GoalsRepositoryProtocol:
    return PostgresGoalsRepository(session)


GoalsRepositoryDep = Annotated[GoalsRepositoryProtocol, Depends(get_goals_repository)]
