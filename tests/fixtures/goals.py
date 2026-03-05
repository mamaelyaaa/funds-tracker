import pytest
from faker import Faker

from domain.goals.entities import Goal
from domain.goals.protocols import GoalsRepositoryProtocol
from domain.goals.service import GoalsService
from domain.values import Title, Money
from infra.repositories.goals import SQLAlchemyGoalRepository


@pytest.fixture
def test_goal(test_user, faker: Faker) -> Goal:
    return Goal.create(
        user_id=test_user.id,
        title=Title(faker.word()),
        target_amount=Money(faker.pyfloat(positive=True)),
    )


@pytest.fixture
def test_goal_repo(test_session) -> GoalsRepositoryProtocol:
    return SQLAlchemyGoalRepository(session=test_session)


@pytest.fixture
def test_goal_service(test_goal_repo) -> GoalsService:
    return GoalsService(goals_repo=test_goal_repo)
