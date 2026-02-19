import pytest

from domain.users.entity import User
from domain.users.repository import UserRepositoryProtocol
from infra.repositories.users import InMemoryUserRepository


@pytest.fixture
async def test_user() -> User:
    return User(name="user-123")


@pytest.fixture
def test_user_repo() -> UserRepositoryProtocol:
    return InMemoryUserRepository()


@pytest.fixture
async def saved_user(test_user, test_user_repo) -> User:
    await test_user_repo.save(test_user)
    return test_user
