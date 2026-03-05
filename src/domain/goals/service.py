from typing import Annotated

from fastapi import Depends

from domain.values import Money, Title
from infra.repositories.goals import GoalsRepositoryDep
from .command import CreateGoalCommand, UpdateGoalPartiallyCommand
from .dto import GoalDTO
from .entities import Goal
from .exceptions import (
    GoalTitleAlreadyTakenException,
    GoalNotFoundException,
)
from .protocols import GoalsRepositoryProtocol


class GoalsService:

    def __init__(self, goals_repo: GoalsRepositoryProtocol):
        self._goals_repo = goals_repo

    async def create_goal(self, command: CreateGoalCommand) -> Goal:
        """Создание цели"""

        # Если название цели для текущего пользователя уже существует, то ошибка
        exists = await self._goals_repo.is_title_taken(
            title=command.title,
            user_id=command.user_id,
        )
        if exists:
            raise GoalTitleAlreadyTakenException

        acc_data = {
            "user_id": command.user_id,
            "title": command.title,
            "target_amount": command.target_amount,
            "current_amount": command.current_amount,
            "deadline": command.deadline,
        }

        goal = Goal.create(**acc_data)

        await self._goals_repo.save(goal)
        return goal

    async def get_user_goals(self, user_id: str) -> list[Goal]:
        """Получение всех целей пользователя"""

        goals = await self._goals_repo.get_by_user_id(user_id)
        return goals

    async def get_user_goal(self, user_id: str, goal_id: str) -> Goal:
        """Получение конкретной цели пользователя"""

        goal = await self._goals_repo.get_by_id(user_id=user_id, goal_id=goal_id)
        if not goal:
            raise GoalNotFoundException
        return goal

    async def update_goal_partially(self, command: UpdateGoalPartiallyCommand) -> Goal:
        """Обновление цели пользователя по полям"""

        goal = await self.get_user_goal(
            goal_id=command.goal_id, user_id=command.user_id
        )

        if command.current_amount:
            goal.current_amount = Money(command.current_amount)

        if command.target_amount:
            goal.target_amount = Money(command.target_amount)

        if command.deadline:
            goal.change_deadline(new_date=command.deadline)

        if command.title:
            goal.title = Title(command.title)

        await self._goals_repo.update(
            goal_id=command.goal_id,
            user_id=command.user_id,
            new_goal=GoalDTO.from_entity_to_dict(goal, excludes=["id", "user_id"]),
        )

        return goal

    async def delete_goal(self, goal_id: str, user_id: str) -> None:
        """Удаление цели пользователя"""

        goal = await self.get_user_goal(goal_id=goal_id, user_id=user_id)
        await self._goals_repo.delete(goal=goal)
        return


def get_goals_service(goals_repo: GoalsRepositoryDep) -> GoalsService:
    return GoalsService(goals_repo=goals_repo)


GoalsServiceDep = Annotated[GoalsService, Depends(get_goals_service)]
