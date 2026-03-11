from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
