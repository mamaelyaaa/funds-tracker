from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport

from infra.repositories.accounts import get_account_repository
from infra.repositories.users import get_user_repository


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
