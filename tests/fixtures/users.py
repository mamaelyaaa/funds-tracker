import pytest

from domain.users.entity import User
from domain.users.protocols import UserRepositoryProtocol
from domain.users.values import Username


@pytest.fixture
async def test_user() -> User:
    return User(username=Username("user-123"), password="secret_pwd")


@pytest.fixture
def test_user_repo(test_session) -> UserRepositoryProtocol:
    from infra.repositories.users import SQLAlchemyUserRepository

    return SQLAlchemyUserRepository(test_session)


@pytest.fixture
async def saved_user(test_user, test_user_repo) -> User:
    await test_user_repo.save(test_user)
    return test_user
