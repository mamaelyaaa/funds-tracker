from unittest.mock import AsyncMock

import pytest

from domain.accounts.commands import UpdateAccountBalanceCommand
from domain.histories.commands import SaveHistoryCommand
from domain.values import Money


@pytest.mark.asyncio
@pytest.mark.history
@pytest.mark.integration
class TestHistoryService:

    async def test_create(
        self, test_user, test_history, test_history_repo, test_history_service
    ):
        """Тест на создание истории"""

        history_id = await test_history_service.save_account_history(
            command=SaveHistoryCommand(
                user_id=test_user.id.as_generic_type(),
                balance=float(test_history.balance.as_generic_type()),
                account_id=test_history.account_id.as_generic_type(),
                is_monthly_closing=test_history.is_monthly_closing,
                created_at=test_history.created_at,
            )
        )

        history_model = await test_history_repo.get_by_id(history_id)
        assert test_history.balance == history_model.balance
        assert test_history.account_id == history_model.account_id
        assert test_history.balance == Money(history_model.delta)

    async def test_history_when_account_update(
        self,
        test_history,
        test_history_repo,
        test_history_service,
        saved_account,
        test_account_service,
    ):

        test_account_service.publisher.publish = AsyncMock()

        await test_account_service.update_balance(
            command=UpdateAccountBalanceCommand(
                account_id=saved_account.id.as_generic_type(),
                user_id=saved_account.user_id.as_generic_type(),
                new_balance=float(saved_account.balance.as_generic_type()) + 100.25,
            )
        )

        exists_acc = await test_account_service.repository.get_by_id(
            user_id=saved_account.user_id.as_generic_type(),
            account_id=test_history.account_id.as_generic_type(),
        )
        # assert len(exists_acc.events) > 1

        test_account_service.publisher.publish.assert_awaited_once()
