import pytest
from faker.proxy import Faker

from domain.histories.entities import History
from domain.histories.protocols import HistoryRepositoryProtocol
from domain.histories.service import HistoryService
from infra.repositories.histories import SQLAlchemyHistoryRepository


@pytest.fixture
def test_history(test_account, faker: Faker) -> History:
    return History(
        account_id=test_account.id,
        balance=test_account.balance,
        is_monthly_closing=faker.boolean(),
    )


@pytest.fixture
def test_history_repo(test_session) -> HistoryRepositoryProtocol:
    return SQLAlchemyHistoryRepository(test_session)


@pytest.fixture
def test_history_service(test_history_repo) -> HistoryService:
    return HistoryService(history_repo=test_history_repo)
