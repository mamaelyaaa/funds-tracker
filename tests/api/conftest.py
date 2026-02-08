from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient, ASGITransport
from taskiq.middlewares.opentelemetry_middleware import retrieve_context

from domain.accounts.entity import Account
from domain.accounts.publisher import AccountEventPublisherProtocol
from domain.accounts.repository import AccountRepositoryProtocol
from domain.accounts.values import Title, AccountCurrency, AccountType
from domain.users.entity import User
from domain.users.repository import UserRepositoryProtocol
from infra.repositories.accounts import get_account_repository
from infra.repositories.users import get_user_repository


@pytest.fixture
def test_account_repo() -> AccountRepositoryProtocol:
    from infra.repositories.accounts import InMemoryAccountRepository

    repo = InMemoryAccountRepository()
    return repo


@pytest.fixture
def test_account_publisher() -> AccountEventPublisherProtocol:
    from infra.publishers.accounts import AccountTaskiqPublisher

    repo = AccountTaskiqPublisher()
    repo.publish = AsyncMock(return_type=None)
    return repo


@pytest.fixture
async def test_account(test_user, test_account_repo) -> Account:
    account = Account.create(
        user_id=test_user.id,
        name=Title("Новый счет"),
        balance=2000,
        currency=AccountCurrency.RUB,
        account_type=AccountType.CARD,
    )
    await test_account_repo.save(account)
    return account


@pytest.fixture
def test_user_repo() -> UserRepositoryProtocol:
    from infra.repositories.users import InMemoryUserRepository

    repo = InMemoryUserRepository()
    return repo


@pytest.fixture
async def test_user(test_user_repo) -> User:
    user = User(name="user-123")
    await test_user_repo.save(user)
    return user


# @pytest.fixture
# def test_history_repo() -> HistoryRepositoryProtocol:
#     from infra.repositories.histories import InMemoryHistoryRepository
#
#     repo = InMemoryHistoryRepository()
#     return repo


@pytest.fixture(autouse=True)
def override_app(test_account_repo, test_user_repo):
    from main import app

    overrides = {
        get_account_repository: lambda: test_account_repo,
        get_user_repository: lambda: test_user_repo,
        # get_history_repository: lambda: test_history_repo,
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
