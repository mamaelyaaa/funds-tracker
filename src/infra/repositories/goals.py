from typing import Optional, Any

from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.goals.entities import Goal
from infra.database.specification import SpecificationProtocol
from infra.models.goals import GoalModel
from .base import SQLAlchemyBaseRepository
from .dto.goals import GoalOrmDTO


class SQLAlchemyGoalRepository(SQLAlchemyBaseRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def save(self, goal: Goal) -> str:
        goal_model: GoalModel = GoalOrmDTO.from_entity_to_orm(goal)
        self.session.add(goal_model)
        await self.session.commit()
        return goal_model.id

    async def get_by_id(self, user_id: str, goal_id: str) -> Optional[Goal]:
        query = select(GoalModel).filter_by(id=goal_id, user_id=user_id)
        goal = await self.session.scalar(query)
        return GoalOrmDTO.from_orm_to_entity(goal) if goal else None

    async def is_title_taken(self, title: str, user_id: str) -> bool:
        query = (
            select(func.count())
            .select_from(GoalModel)
            .filter_by(title=title, user_id=user_id)
        )
        res = await self.session.execute(query)
        return bool(res.scalar_one())

    async def count_by_user_id(self, user_id: str) -> int:
        query = select(func.count()).select_from(GoalModel).filter_by(user_id=user_id)
        res = await self.session.execute(query)
        return res.scalar_one()

    async def count(self) -> int:
        query = select(func.count()).select_from(GoalModel)
        res = await self.session.execute(query)
        return res.scalar_one()

    async def get_by_user_id(
        self, user_id: str, *specs: SpecificationProtocol
    ) -> list[Goal]:
        query = select(GoalModel).filter_by(user_id=user_id)
        query = self._apply_specs(query, specs)
        res = await self.session.execute(query)
        return [GoalOrmDTO.from_orm_to_entity(row) for row in res.scalars()]

    async def get_by_user_id_except_goal_id(
        self, user_id: str, goal_id: str
    ) -> list[Goal]:
        query = (
            select(GoalModel).filter_by(user_id=user_id).where(GoalModel.id != goal_id)
        )
        res = await self.session.execute(query)
        return [GoalOrmDTO.from_orm_to_entity(row) for row in res.scalars()]

    async def delete(self, goal: Goal) -> None:
        stmt = delete(GoalModel).filter_by(
            id=goal.id.as_generic_type(),
            user_id=goal.user_id.as_generic_type(),
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def update(
        self, user_id: str, goal_id: str, upd_data: dict[str, Any], commit: bool
    ) -> Optional[Goal]:
        stmt = (
            update(GoalModel)
            .filter_by(id=goal_id, user_id=user_id)
            .values(**upd_data)
            .returning(GoalModel)
        )
        goal = await self.session.scalar(stmt)
        if commit:
            await self.session.commit()
        return GoalOrmDTO.from_orm_to_entity(goal) if goal else None

    async def check_exists_by_id(self, user_id: str, account_id: str) -> bool:
        query = (
            select(func.count())
            .select_from(GoalModel)
            .filter_by(user_id=user_id, id=account_id)
        )
        res = await self.session.scalar(query)
        return bool(res)
