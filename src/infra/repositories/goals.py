from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.goals.entities import Goal
from infra.models.goals import GoalModel
from .base import SQLAlchemyBaseRepository
from .dto.goals import GoalOrmDTO


class SQLAlchemyGoalRepository(SQLAlchemyBaseRepository[GoalModel, Goal]):
    """Репозиторий для работы с целями пользователей"""

    model = GoalModel
    dto = GoalOrmDTO

    def __init__(self, session: AsyncSession):
        super().__init__(session)

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

    async def get_by_user_id_except_goal_id(
        self, user_id: str, goal_id: str
    ) -> list[Goal]:
        query = (
            select(GoalModel).filter_by(user_id=user_id).where(GoalModel.id != goal_id)
        )
        res = await self.session.execute(query)
        return [GoalOrmDTO.from_orm_to_entity(row) for row in res.scalars()]

    async def check_exists_by_id(self, user_id: str, account_id: str) -> bool:
        query = (
            select(func.count())
            .select_from(GoalModel)
            .filter_by(user_id=user_id, id=account_id)
        )
        res = await self.session.scalar(query)
        return bool(res)
