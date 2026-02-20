from typing import Annotated

from fastapi import Depends

from infra.repositories.goals import GoalsRepositoryDep
from .command import CreateGoalCommand, UpdateGoalPartiallyCommand
from .dto import GoalDTO
from .entities import Goal
from .exceptions import (
    GoalTitleAlreadyTakenException,
    GoalNotFoundException,
    GoalsPercentageOutOfBoundsException,
)
from .protocols import GoalsRepositoryProtocol
from .values import GoalPercentage


class GoalsService:

    def __init__(
        self,
        goals_repo: GoalsRepositoryProtocol,
    ):
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

        # Если процентное соотношение превышает 100% - ошибка
        if command.savings_percentage:
            goals = await self.get_user_goals(user_id=command.user_id)
            if (
                command.savings_percentage
                + sum(goal.savings_percentage.as_generic_type() for goal in goals)
                > 1
            ):
                raise GoalsPercentageOutOfBoundsException

        acc_data = {
            "user_id": command.user_id,
            "account_id": command.account.id if command.account else None,
            "title": command.title,
            "target_amount": command.target_amount,
            "savings_percentage": command.savings_percentage,
            "deadline": command.deadline,
        }

        goal = Goal.create(**acc_data)

        # Если цель привязывается к счёту, то текущий баланс берется из баланса счёта
        if command.account:
            goal.change_current_amount(new_current=command.account.balance)

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
            goal.change_current_amount(new_current=command.current_amount)

        if command.target_amount:
            goal.change_target_amount(new_target=command.target_amount)

        if command.deadline:
            goal.change_deadline(new_date=command.deadline)

        if command.savings_percentage:
            goals = await self._goals_repo.get_by_user_id_except_goal_id(
                user_id=command.user_id,
                goal_id=command.goal_id,
            )
            if (
                command.savings_percentage
                + sum(goal.savings_percentage.as_generic_type() for goal in goals)
                > 1
            ):
                raise GoalsPercentageOutOfBoundsException

            goal.change_percentage(
                new_percentage=GoalPercentage(command.savings_percentage)
            )

        if command.unlink_account:
            goal.unlink_account()

        if command.account:
            goal.link_to_account(account_id=command.account.id)
            goal.change_current_amount(new_current=command.account.balance)

        if command.title:
            goal.change_title(new_title=command.title)

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
