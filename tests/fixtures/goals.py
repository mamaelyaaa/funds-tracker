import pytest
from faker import Faker

from domain.goals.entities import Goal
from domain.goals.protocols import GoalsRepositoryProtocol, GoalsEventPublisherProtocol
from domain.goals.service import GoalsService
from infra.publishers.goals import GoalsTaskiqPublisher
from infra.repositories.goals import InMemoryGoalsRepository


@pytest.fixture
def test_goal(faker: Faker) -> Goal:
    return Goal.create(
        user_id="user-123",
        title=faker.word(),
        target_amount=faker.pyfloat(positive=True),
    )


@pytest.fixture
def test_goals_repository() -> GoalsRepositoryProtocol:
    return InMemoryGoalsRepository()


@pytest.fixture
def test_goals_publisher() -> GoalsEventPublisherProtocol:
    return GoalsTaskiqPublisher()


@pytest.fixture
def test_goals_service(
    test_goals_repository,
    # test_goals_publisher,
) -> GoalsService:
    return GoalsService(
        goals_repo=test_goals_repository,
        # goal_event_publisher=test_goals_publisher,
        # account_repo=test_account_repo,
    )
