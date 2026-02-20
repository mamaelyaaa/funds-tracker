from datetime import datetime, timedelta

import pytest
from faker.proxy import Faker

from domain.goals.command import CreateGoalCommand, UpdateGoalPartiallyCommand
from domain.goals.entities import Goal
from domain.goals.exceptions import (
    GoalTitleAlreadyTakenException,
    GoalsPercentageOutOfBoundsException,
    GoalNotFoundException,
    InvalidGoalAmountsException,
    InvalidGoalPercentageException,
)


@pytest.mark.asyncio
@pytest.mark.goals
@pytest.mark.integration
class TestGoalsService:

    async def test_goals_service_create_success(
        self,
        test_goal,
        test_goal_service,
        test_goal_repo,
    ):
        """Успешное создание цели с помощью сервиса"""

        goal = await test_goal_service.create_goal(
            command=CreateGoalCommand(
                title=test_goal.title.as_generic_type(),
                target_amount=test_goal.target_amount,
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

        assert await test_goal_repo.count() == 1

        with pytest.raises(GoalTitleAlreadyTakenException):
            await test_goal_service.create_goal(
                command=CreateGoalCommand(
                    user_id=test_goal.user_id.as_generic_type(),
                    title=test_goal.title.as_generic_type(),
                    target_amount=test_goal.target_amount,
                )
            )

        assert await test_goal_repo.count() == 1

    async def test_goal_percentage_out_of_bounds(
        self,
        faker: Faker,
        test_goal,
        test_goal_repo,
        test_goal_service,
    ):
        """Пользователю необходимо перераспределить проценты на цели"""

        await test_goal_repo.save(test_goal)

        with pytest.raises(GoalsPercentageOutOfBoundsException):
            await test_goal_service.create_goal(
                command=CreateGoalCommand(
                    user_id=test_goal.user_id.as_generic_type(),
                    title=faker.word(),
                    target_amount=test_goal.target_amount,
                    savings_percentage=test_goal.savings_percentage.as_generic_type()
                    + 1,
                )
            )

        assert await test_goal_repo.count() == 1

        await test_goal_service.create_goal(
            command=CreateGoalCommand(
                user_id=test_goal.user_id.as_generic_type(),
                title=faker.word(),
                target_amount=test_goal.target_amount,
                savings_percentage=1 - test_goal.savings_percentage.as_generic_type(),
            )
        )

        assert await test_goal_repo.count() == 2

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
                    user_id="user-123",
                    title=faker.word(),
                    target_amount=faker.pyfloat(positive=True),
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
            {"deadline": datetime.now() + timedelta(days=30)},
            {"savings_percentage": 0.25},
            # 2. Обновление нескольких полей
            {
                "title": "Обновленный заголовок",
                "current_amount": 7500.0,
            },
            {
                "target_amount": 150000.0,
                "deadline": datetime.now() + timedelta(days=60),
            },
            # 3. Обновление всех полей сразу
            {
                "title": "Полное обновление",
                "current_amount": 10000.0,
                "target_amount": 200000.0,
                "deadline": datetime.now() + timedelta(days=90),
                "savings_percentage": 0.5,
            },
            # 4. Граничные значения процента
            {"savings_percentage": 0.01},
            {"savings_percentage": 1.0},  # 100%
            # 5. Удаление привязки к счету
            {"unlink_account": True},
            # 7. Обновление с None значениями
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
                InvalidGoalAmountsException,
            ),  # Отрицательная сумма
            (
                {"savings_percentage": -0.1},
                InvalidGoalPercentageException,
            ),  # Отрицательный процент
            (
                {"savings_percentage": 1.5},
                GoalsPercentageOutOfBoundsException,
            ),  # Процент больше 100%
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

    async def test_link_account_id_success(
        self,
        test_goal,
        test_goal_repo,
        test_goal_service,
        test_account,
        test_account_repo,
    ):
        """Привязка счета к текущей цели"""

        # Сохраняем цель пользователя
        await test_goal_repo.save(test_goal)

        acc_id = await test_account_repo.save(test_account)
        exists_acc = await test_account_repo.get_by_id(
            account_id=acc_id,
            user_id=test_account.user_id.as_generic_type(),
        )
        assert exists_acc.id.as_generic_type() == acc_id

        upd_goal = await test_goal_service.update_goal_partially(
            command=UpdateGoalPartiallyCommand(
                account=exists_acc,
                goal_id=test_goal.id.as_generic_type(),
                user_id=test_goal.user_id.as_generic_type(),
            )
        )
        assert upd_goal.account_id.as_generic_type() == exists_acc.id.as_generic_type()

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
