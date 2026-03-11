from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from faker.proxy import Faker

from domain.goals.entities import Goal


@pytest.mark.asyncio
@pytest.mark.goals
@pytest.mark.api
class TestGoalApi:

    @pytest.mark.parametrize(
        "json",
        [
            # Создание без привязки к счёту
            (
                {
                    "title": "На подушку",
                    "targetAmount": 1000,
                    "currentAmount": 0,
                    "deadline": (
                        datetime.now(timezone.utc) + timedelta(days=30)
                    ).isoformat(),
                }
            ),
            # Создание без указания дедлайна
            (
                {
                    "title": "На подушку",
                    "targetAmount": 1000,
                    "currentAmount": 0,
                    "deadline": None,
                }
            ),
        ],
    )
    async def test_create_success(self, client, saved_user, json):
        """Тест успешное создание цели"""

        response = await client.post(
            url=f"/api/v1/users/{saved_user.id.as_generic_type()}/goals", json=json
        )

        assert response.status_code == 201
        assert "успешно создана" in response.json()["message"]

        detail: dict = response.json()["detail"]
        assert detail.get("userId") == saved_user.id.as_generic_type()
        assert "createdAt" in detail

    @pytest.mark.parametrize(
        "test_field, expected_status",
        [
            # Невалидное название по размеру
            (
                {
                    "title": "AAA" * 60,
                },
                400,
            ),
            # Невалидное название по символам
            (
                {
                    "title": "^&*^*@$",
                },
                400,
            ),
            # Дедлайн до текущей даты
            (
                {
                    "deadline": (
                        datetime.now(timezone.utc) - timedelta(days=30)
                    ).isoformat(),
                },
                400,
            ),
            # Отрицательная цель
            (
                {
                    "targetAmount": -1,
                },
                400,
            ),
        ],
    )
    async def test_input_values_in_creation(
        self,
        client,
        faker: Faker,
        saved_account,
        test_field: dict[str, Any],
        expected_status: int,
    ):
        """Проверка на валидность входных данных при создании"""

        json = {
            "title": faker.word(),
            "targetAmount": faker.pyfloat(positive=True),
            "currentAmount": 0,
            "deadline": None,
        }
        json.update(test_field)

        response = await client.post(
            url=f"/api/v1/users/{saved_account.user_id.as_generic_type()}/goals",
            json=json,
        )

        assert response.status_code == expected_status

    async def test_get_goals(self, client, saved_user, test_goal, test_goal_repo):
        """Тест получение всех целей пользователя"""

        goal_id = await test_goal_repo.save(test_goal)
        exists_goal = await test_goal_repo.get_by_id(
            user_id=saved_user.id.as_generic_type(), goal_id=goal_id
        )

        response = await client.get(
            url=f"/api/v1/users/{saved_user.id.as_generic_type()}/goals"
        )

        assert response.status_code == 200
        detail: list[dict] = response.json()["detail"]

        goal: dict = detail[0]
        assert goal.get("id") == goal_id
        assert goal.get("currentAmount") == exists_goal.current_amount.as_generic_type()
        assert goal.get("title") == exists_goal.title.as_generic_type()
        assert "createdAt" in goal

    @pytest.fixture
    async def saved_goal(self, saved_user, test_goal, test_goal_repo) -> Goal:
        await test_goal_repo.save(test_goal)
        return test_goal

    async def test_get_goal_success(self, client, saved_goal):
        """Тест цель найдена"""

        response = await client.get(
            url=f"/api/v1/users/{saved_goal.user_id.as_generic_type()}/goals/{saved_goal.id.as_generic_type()}"
        )

        assert response.status_code == 200
        detail: dict = response.json()["detail"]

        assert detail["id"] == saved_goal.id.as_generic_type()
        assert detail["title"] == saved_goal.title.as_generic_type()
        assert "createdAt" in detail

    async def test_get_goal_by_id_not_found(self, client, saved_goal):
        """Тест цель не найдена"""

        response = await client.get(
            url=f"/api/v1/users/{saved_goal.user_id.as_generic_type()}/goals/unknown-goal-id"
        )

        assert response.status_code == 404
        assert "не найден" in response.json()["message"]

    async def test_delete_success(self, client, saved_goal):
        """Тест удаление цели"""
        response = await client.delete(
            url=f"/api/v1/users/{saved_goal.user_id.as_generic_type()}/goals/{saved_goal.id.as_generic_type()}"
        )
        assert response.status_code == 204
