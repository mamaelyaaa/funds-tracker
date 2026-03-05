import pytest

from core.settings import settings
from infra import db_helper
from infra.models import Base
from .fixtures import *  # noqa


@pytest.fixture(autouse=True, scope="session")
async def setup_tests():
    assert settings.app.env == "TEST"
    assert "aiosqlite" in str(db_helper.engine.url)

    yield

    await db_helper.dispose()


@pytest.fixture(autouse=True)
async def setup_db():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        yield


@pytest.fixture
async def test_session():
    async with db_helper.session_factory() as session:
        yield session
