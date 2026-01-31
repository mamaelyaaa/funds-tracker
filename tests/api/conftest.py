from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport

from infra.cache.accounts import get_account_cache, InMemoryAccountCache
from infra.publishers.accounts import (
    get_account_event_publisher,
    AccountTaskiqPublisher,
)
from infra.repositories.accounts import (
    InMemoryAccountRepository,
    get_account_repository,
)
from infra.repositories.users import get_user_repository, InMemoryUserRepository
from src.main import app


@pytest.fixture
def test_user_repository():
    repo = InMemoryUserRepository()
    yield repo


@pytest.fixture
def test_account_repository():
    repo = InMemoryAccountRepository()
    yield repo


@pytest.fixture
def test_account_cache():
    repo = InMemoryAccountCache()
    yield repo


@pytest.fixture
def test_account_event_publisher():
    repo = AccountTaskiqPublisher()
    yield repo


@pytest.fixture
async def test_app(
    test_user_repository,
    test_account_repository,
    test_account_cache,
    test_account_event_publisher,
):

    async def override_get_user_repository():
        return test_user_repository

    async def override_get_account_repository():
        return test_account_repository

    async def override_get_account_cache():
        return test_account_cache

    async def override_get_account_event_publisher():
        return test_account_event_publisher

    app.dependency_overrides[get_user_repository] = override_get_user_repository
    app.dependency_overrides[get_account_repository] = override_get_account_repository
    app.dependency_overrides[get_account_event_publisher] = (
        override_get_account_event_publisher
    )
    app.dependency_overrides[get_account_cache] = override_get_account_cache

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
async def client(test_app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client
