from datetime import datetime, timedelta
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
                    "accountId": None,
                    "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
                    "savingsPercentage": 0.2,
                }
            ),
            # Создание без указания дедлайна
            (
                {
                    "title": "На подушку",
                    "targetAmount": 1000,
                    "accountId": None,
                    "deadline": None,
                    "savingsPercentage": 0.5,
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

    async def test_create_with_account_link(
        self,
        client,
        faker: Faker,
        saved_account,
    ):
        """Тест успешное создание с привязкой счёта"""

        response = await client.post(
            url=f"/api/v1/users/{saved_account.user_id.as_generic_type()}/goals",
            json={
                "title": faker.word(),
                "targetAmount": faker.pyfloat(positive=True),
                "accountId": saved_account.id.as_generic_type(),
                "deadline": None,
                "savingsPercentage": 0.5,
            },
        )

        assert response.status_code == 201

        detail: dict = response.json()["detail"]
        assert detail.get("accountId") == saved_account.id.as_generic_type()
        assert detail.get("currentAmount") == saved_account.balance.as_generic_type()

    async def test_create_with_unknown_account(
        self,
        client,
        faker: Faker,
        saved_account,
    ):
        """Тест создание цели с привязкой к несуществующему счёту"""
        response = await client.post(
            url=f"/api/v1/users/{saved_account.user_id.as_generic_type()}/goals",
            json={
                "title": faker.word(),
                "targetAmount": faker.pyfloat(positive=True),
                "accountId": "unknown-acc-id",
                "deadline": None,
                "savingsPercentage": 0.5,
            },
        )

        assert response.status_code == 404
        assert "не найден" in response.json().get("message")

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
                    "deadline": (datetime.now() - timedelta(days=30)).isoformat(),
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
            # Процентное соотношение больше 100% (>1)
            (
                {
                    "savingsPercentage": 1.1,
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
            "accountId": None,
            "deadline": None,
            "savingsPercentage": 0.5,
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
        assert (
            detail["savingsPercentage"]
            == saved_goal.savings_percentage.as_generic_type()
        )
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
