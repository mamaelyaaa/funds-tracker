import pytest

from core.settings import settings
from .fixtures import *  # noqa


@pytest.fixture(autouse=True)
def setup_tests():
    assert settings.app.env == "TEST"
    yield
