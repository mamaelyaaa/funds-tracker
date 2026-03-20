import asyncio
from dataclasses import asdict

from api.schemas import PaginationMetaSchema
from domain.users.values import UserId
from domain.values import Money, Title
from infra.database.specification import PaginationSpecification
from .command import (
    CreateGoalCommand,
    UpdateGoalPartiallyCommand,
    GetGoalsCommand,
    GetGoalCommand,
)
from .dto import GoalDTO
from .entities import Goal
from .exceptions import GoalTitleAlreadyTakenException, GoalNotFoundException
from .protocols import GoalRepositoryProtocol


class GoalService:
    """Сервис для работы с целями пользователей"""

    def __init__(self, goals_repo: GoalRepositoryProtocol):
        self.goal_repo = goals_repo

    async def create_goal(self, command: CreateGoalCommand) -> Goal:
        """Создание цели"""

        # Если название цели для текущего пользователя уже существует, то ошибка
        exists = await self.goal_repo.is_title_taken(
            title=command.title,
            user_id=command.user_id,
        )
        if exists:
            raise GoalTitleAlreadyTakenException

        acc_data = {
            "user_id": UserId(command.user_id),
            "title": Title(command.title),
            "target_amount": Money(command.target_amount),
            "current_amount": Money(command.current_amount),
            "deadline": command.deadline,
        }
        goal = Goal(**acc_data)

        await self.goal_repo.save(goal)
        return goal

    async def get_user_goals(self, command: GetGoalsCommand) -> tuple[
        list[Goal],
        PaginationMetaSchema,
    ]:
        """Получение всех целей пользователя"""

        goals = await self.goal_repo.find_all(
            PaginationSpecification.from_pagination_command(command.pagination),
            user_id=command.user_id,
        )
        goals_count = await self.goal_repo.count_by_user_id(command.user_id)

        return goals, PaginationMetaSchema(
            total_found=goals_count,
            **asdict(command.pagination),
        )

    async def get_user_goal(self, command: GetGoalCommand) -> Goal:
        """Получение конкретной цели пользователя"""

        goal = await self.goal_repo.find_one(
            id=command.goal_id,
            user_id=command.user_id,
        )
        if not goal:
            raise GoalNotFoundException
        return goal

    async def update_goal_partially(self, command: UpdateGoalPartiallyCommand) -> Goal:
        """Обновление цели пользователя по полям"""

        goal = await self.get_user_goal(
            GetGoalCommand(goal_id=command.goal_id, user_id=command.user_id)
        )

        if command.current_amount:
            goal.current_amount = Money(command.current_amount)

        if command.target_amount:
            goal.target_amount = Money(command.target_amount)

        if command.deadline:
            goal.change_deadline(new_date=command.deadline)

        if command.title:
            goal.title = Title(command.title)

        await self.goal_repo.update(
            id=command.goal_id,
            user_id=command.user_id,
            upd_data=GoalDTO.from_entity_to_dict(goal, excludes=["id", "user_id"]),
        )

        return goal

    async def delete_goal(self, command: GetGoalCommand) -> None:
        """Удаление цели пользователя"""

        goal = await self.get_user_goal(command)
        await self.goal_repo.delete_one(id=goal.id, user_id=goal.user_id)
        return
