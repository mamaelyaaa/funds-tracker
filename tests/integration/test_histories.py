from datetime import timedelta
from unittest.mock import AsyncMock

import pytest

from domain.accounts.values import AccountId
from domain.histories.commands import SaveHistoryCommand
from domain.histories.domain import History
from domain.histories.repository import HistoryRepositoryProtocol
from domain.histories.service import HistoryService
from domain.histories.values import HistoryId
from infra.repositories.histories import InMemoryHistoryRepository


@pytest.fixture
def mock_history_entity() -> History:
    return History.create(
        account_id=AccountId("acc-123"),
        balance=150,
    )


@pytest.fixture
def mock_history_repo(mock_history_entity) -> HistoryRepositoryProtocol:
    repo = InMemoryHistoryRepository()
    return repo


@pytest.fixture
def mock_history_service(mock_history_repo) -> HistoryService:
    return HistoryService(mock_history_repo)


@pytest.mark.asyncio
@pytest.mark.integration
class TestHistoryService:

    async def test_make_history_screenshot_success(
        self, mock_history_service, mock_history_entity, mock_history_repo
    ):
        """Тест на создание новой записи истории аккаунта"""

        history_id = await mock_history_service.save_account_history(
            command=SaveHistoryCommand(
                account_id=mock_history_entity.account_id.value,
                balance=mock_history_entity.balance,
            )
        )

        assert await mock_history_repo.get_by_id(HistoryId(history_id)) is not None

    async def test_history_make_screenshot_time_limit_creation(
        self, mock_history_service, mock_history_entity, mock_history_repo
    ):
        """Тест на обновление истории с учетом лимита времени для создания"""

        mock_history_repo.get_acc_by_acc_id_with_time_limit = AsyncMock(
            return_value=mock_history_entity
        )

        history_id = await mock_history_service.save_account_history(
            command=SaveHistoryCommand(
                account_id=mock_history_entity.account_id.value,
                balance=1000,
            )
        )

        new_history = await mock_history_repo.get_by_id(HistoryId(history_id))

        assert new_history.id == mock_history_entity.id
        assert new_history.balance == 1000
        assert new_history.balance != mock_history_entity.balance
        assert new_history.created_at > mock_history_entity.created_at
