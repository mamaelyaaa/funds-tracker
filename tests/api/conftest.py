from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport

from domain.users.entity import User
from infra.repositories.accounts import (
    get_account_repository,
)
from infra.repositories.users import get_user_repository


@pytest.fixture
def test_account_repo():
    from infra.repositories.accounts import InMemoryAccountRepository

    repo = InMemoryAccountRepository()
    yield repo
    repo.clear()


@pytest.fixture
def test_user_repo():
    from infra.repositories.users import InMemoryUserRepository

    repo = InMemoryUserRepository()
    yield repo
    repo.clear()


@pytest.fixture
async def test_user(test_user_repo):
    user = User(name="user-123")
    await test_user_repo.save(user)
    return user


@pytest.fixture(autouse=True)
def override_app(
    test_account_repo,
    test_user_repo,
):
    from src.main import app

    overrides = {
        get_account_repository: lambda: test_account_repo,
        get_user_repository: lambda: test_user_repo,
    }

    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides.update(overrides)

    yield app

    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


@pytest.fixture
async def client(override_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=override_app),
        base_url="http://test",
    ) as client:
        yield client
