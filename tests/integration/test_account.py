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
            user_id=test_account.user_id.as_generic_type(),
            name=test_account.name.as_generic_type(),
            balance=test_account.balance.as_generic_type(),
            account_type=test_account.type,
            currency=test_account.currency,
        )
    )

    exists_acc = await test_account_repo.get_by_id(
        user_id=account.user_id.as_generic_type(),
        account_id=account.id.as_generic_type(),
    )
    assert account == exists_acc

    test_account_publisher.publish.assert_awaited_once()
