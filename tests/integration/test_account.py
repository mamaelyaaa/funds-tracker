from unittest.mock import AsyncMock

import pytest

from domain.accounts.commands import CreateAccountCommand


@pytest.mark.asyncio
@pytest.mark.accounts
@pytest.mark.integration
async def test_create_account(
    test_account,
    test_account_repo,
    test_account_publisher: AsyncMock,
    test_account_service,
):
    """Тест счёт успешно создан"""

    account = await test_account_service.create_account(
        command=CreateAccountCommand(
            user_id=test_account.user_id.value,
            name=test_account.name.value,
            balance=test_account.balance,
            account_type=test_account.type,
            currency=test_account.currency,
        )
    )

    exists_acc = await test_account_repo.get_by_id(
        user_id=account.user_id, account_id=account.id
    )
    assert account == exists_acc

    test_account_publisher.publish.assert_awaited_once()
