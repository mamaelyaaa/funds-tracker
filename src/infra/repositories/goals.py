from typing import Optional, Annotated, Any

from fastapi import Depends
from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.goals.entities import Goal
from domain.goals.protocols import GoalsRepositoryProtocol
from domain.goals.values import GoalId
from infra.database import SessionDep
from infra.models.goals import GoalModel
from .base import BaseInMemoryRepository
from .dto.goals import GoalDTO


class InMemoryGoalsRepository(BaseInMemoryRepository[GoalId, Goal]):

    async def save(self, goal: Goal) -> None:
        self._storage[goal.id] = goal

    async def get_by_id(self, goal_id: str) -> Optional[Goal]:
        return self._storage.get(GoalId(goal_id), None)

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

    async def delete(self, goal: Goal) -> None:
        self._storage.pop(goal.id)

    async def update(self, goal_id: str, new_goal: dict[str, Any]) -> Goal:
        exists_goal = await self.get_by_id(goal_id)

        for key, val in new_goal.items():
            if hasattr(exists_goal, key):
                setattr(exists_goal, key, val)

        return exists_goal


class PostgresGoalsRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, goal: Goal) -> None:
        goal_model = GoalDTO.to_orm(goal)
        self._session.add(goal_model)
        await self._session.commit()

    async def get_by_id(self, goal_id: str) -> Optional[Goal]:
        query = select(GoalModel).filter_by(id=goal_id)
        goal = await self._session.scalar(query)
        return GoalDTO.to_entity(goal) if goal else None

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
        return [GoalDTO.to_entity(row) for row in res.scalars()]

    async def get_by_user_id_except_goal_id(
        self, user_id: str, goal_id: str
    ) -> list[Goal]:
        query = (
            select(GoalModel).filter_by(user_id=user_id).where(GoalModel.id != goal_id)
        )
        res = await self._session.execute(query)
        return [GoalDTO.to_entity(row) for row in res.scalars()]

    async def delete(self, goal: Goal) -> None:
        stmt = delete(GoalModel).where(
            user_id=goal.user_id.as_generic_type(),
            goal_id=goal.id.as_generic_type(),
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def update(self, goal_id: str, new_goal: dict[str, Any]) -> Goal:
        stmt = (
            update(GoalModel)
            .filter_by(id=goal_id)
            .values(**new_goal)
            .returning(GoalModel)
        )
        res = await self._session.execute(stmt)
        await self._session.commit()
        return GoalDTO.to_entity(res.scalar_one())


def get_goals_repository(session: SessionDep) -> GoalsRepositoryProtocol:
    return PostgresGoalsRepository(session)


GoalsRepositoryDep = Annotated[GoalsRepositoryProtocol, Depends(get_goals_repository)]
