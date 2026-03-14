import pytest
from faker import Faker

from api.v1.dependencies.goals import get_goal_service
from domain.goals.entities import Goal
from domain.goals.protocols import GoalRepositoryProtocol
from domain.goals.service import GoalService
from domain.values import Title, Money


@pytest.fixture
def test_goal(test_user, faker: Faker) -> Goal:
    return Goal.create(
        user_id=test_user.id,
        title=Title(faker.word()),
        target_amount=Money(faker.pyfloat(positive=True)),
    )


@pytest.fixture
def test_goal_repo(test_session) -> GoalRepositoryProtocol:
    from infra.repositories.goals import SQLAlchemyGoalRepository

    return SQLAlchemyGoalRepository(session=test_session)


@pytest.fixture
async def saved_goal(test_goal, test_goal_repo) -> Goal:
    await test_goal_repo.save(test_goal)
    return test_goal


@pytest.fixture
def test_goal_service(test_session) -> GoalService:
    goal_service = get_goal_service(test_session)
    return goal_service
