from datetime import datetime, timedelta, timezone

import pytest
from faker.proxy import Faker

from domain.exceptions import InvalidBalanceException
from domain.goals.command import CreateGoalCommand, UpdateGoalPartiallyCommand
from domain.goals.entities import Goal
from domain.goals.exceptions import (
    GoalTitleAlreadyTakenException,
    GoalNotFoundException,
)
from domain.users.values import UserId
from domain.values import Title, Money


@pytest.mark.asyncio
@pytest.mark.goals
@pytest.mark.integration
class TestGoalsService:

    async def test_create_success(
        self,
        test_goal,
        test_goal_repo,
        test_goal_service,
    ):
        """Успешное создание цели с помощью сервиса"""

        goal = await test_goal_service.create_goal(
            command=CreateGoalCommand(
                title=test_goal.title.as_generic_type(),
                target_amount=float(test_goal.target_amount.as_generic_type()),
                user_id=test_goal.user_id.as_generic_type(),
            )
        )

        saved_goal = await test_goal_repo.get_by_id(
            goal_id=goal.id.as_generic_type(), user_id=goal.user_id.as_generic_type()
        )
        assert goal == saved_goal

    async def test_goal_title_already_taken(
        self,
        test_goal,
        test_goal_repo,
        test_goal_service,
    ):
        """Цель с таким названием уже имеется у пользователя"""

        await test_goal_repo.save(test_goal)

        with pytest.raises(GoalTitleAlreadyTakenException):
            await test_goal_service.create_goal(
                command=CreateGoalCommand(
                    user_id=test_goal.user_id.as_generic_type(),
                    title=test_goal.title.as_generic_type(),
                    target_amount=float(test_goal.target_amount.as_generic_type()),
                )
            )

        assert await test_goal_repo.count() == 1

    async def test_user_goal_success(
        self,
        test_goal,
        test_goal_service,
        test_goal_repo,
    ):
        """Успешное получение цели пользователя"""

        await test_goal_repo.save(test_goal)

        saved_goal = await test_goal_service.get_user_goal(
            goal_id=test_goal.id.as_generic_type(),
            user_id=test_goal.user_id.as_generic_type(),
        )
        assert saved_goal == test_goal

    async def test_user_goal_not_found(
        self,
        test_goal,
        test_goal_service,
        test_goal_repo,
    ):
        """Цель пользователя не найдена"""

        assert await test_goal_repo.count() == 0

        with pytest.raises(GoalNotFoundException):
            await test_goal_service.get_user_goal(
                goal_id=test_goal.id.as_generic_type(),
                user_id=test_goal.user_id.as_generic_type(),
            )

    async def test_user_goals_success(
        self,
        faker: Faker,
        test_goal,
        test_goal_service,
        test_goal_repo,
    ):
        """Успешное получение всех целей пользователя"""

        for _ in range(5):
            await test_goal_repo.save(
                Goal.create(
                    user_id=UserId("user-123"),
                    title=Title(faker.word()),
                    target_amount=Money(faker.pyfloat(positive=True)),
                )
            )

        saved_goals = await test_goal_service.get_user_goals(user_id="user-123")

        assert len(saved_goals) == 5

    @pytest.mark.parametrize(
        "fields_to_update",
        [
            # 1. Обновление каждого поля по отдельности
            {"title": "Новое название"},
            {"current_amount": 5000.0},
            {"target_amount": 100000.0},
            {"deadline": datetime.now(timezone.utc) + timedelta(days=30)},
            # {"savings_percentage": 0.25},
            # 2. Обновление нескольких полей
            {
                "title": "Обновленный заголовок",
                "current_amount": 7500.0,
            },
            {
                "target_amount": 150000.0,
                "deadline": datetime.now(timezone.utc) + timedelta(days=60),
            },
            # 3. Обновление всех полей сразу
            {
                "title": "Полное обновление",
                "current_amount": 10000.0,
                "target_amount": 200000.0,
                "deadline": datetime.now(timezone.utc) + timedelta(days=90),
            },
            # 4. Обновление с None значениями
            {"title": None, "current_amount": None},
        ],
    )
    async def test_update_goal(
        self,
        test_goal,
        test_goal_service,
        test_goal_repo,
        fields_to_update,
    ):

        await test_goal_repo.save(test_goal)

        upd_goal = await test_goal_service.update_goal_partially(
            command=UpdateGoalPartiallyCommand(
                goal_id=test_goal.id.as_generic_type(),
                user_id=test_goal.user_id.as_generic_type(),
                **fields_to_update,
            )
        )

        saved_goal = await test_goal_repo.get_by_id(
            goal_id=upd_goal.id.as_generic_type(),
            user_id=upd_goal.user_id.as_generic_type(),
        )
        assert saved_goal == upd_goal

    @pytest.mark.parametrize(
        "fields_to_update, expected_error",
        [
            (
                {"current_amount": -100},
                InvalidBalanceException,
            ),  # Отрицательная сумма
            # (
            # {"savings_percentage": -0.1},
            # InvalidGoalPercentageException,
            # ),  # Отрицательный процент
            # (
            # {"savings_percentage": 1.5},
            # GoalsPercentageOutOfBoundsException,
            # ),  # Процент больше 100%
        ],
    )
    async def test_update_goal_partially_errors(
        self,
        test_goal,
        test_goal_service,
        test_goal_repo,
        fields_to_update,
        expected_error,
    ):
        """Проверяем обработку ошибок при некорректных данных."""

        await test_goal_repo.save(test_goal)

        with pytest.raises(expected_error):
            await test_goal_service.update_goal_partially(
                command=UpdateGoalPartiallyCommand(
                    goal_id=test_goal.id.as_generic_type(),
                    user_id=test_goal.user_id.as_generic_type(),
                    **fields_to_update,
                )
            )

    async def test_goal_delete_success(
        self,
        test_goal,
        test_goal_service,
        test_goal_repo,
    ):
        await test_goal_repo.save(test_goal)
        assert await test_goal_repo.count() == 1

        await test_goal_service.delete_goal(
            goal_id=test_goal.id.as_generic_type(),
            user_id=test_goal.user_id.as_generic_type(),
        )

        assert await test_goal_repo.count() == 0
