import pytest
from faker import Faker

from domain.goals.entities import Goal
from domain.goals.protocols import GoalsRepositoryProtocol
from domain.goals.service import GoalsService
from infra.repositories.goals import InMemoryGoalsRepository


@pytest.fixture
def test_goal(test_user, faker: Faker) -> Goal:
    return Goal.create(
        user_id=test_user.id.as_generic_type(),
        title=faker.word(),
        target_amount=faker.pyfloat(positive=True),
    )


@pytest.fixture
def test_goal_repo() -> GoalsRepositoryProtocol:
    return InMemoryGoalsRepository()


@pytest.fixture
def test_goal_service(test_goal_repo) -> GoalsService:
    return GoalsService(goals_repo=test_goal_repo)
