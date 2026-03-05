from copy import copy
from unittest.mock import AsyncMock

import pytest
from faker.proxy import Faker

from domain.accounts.commands import CreateAccountCommand, UpdateAccountBalanceCommand
from domain.accounts.exceptions import AccountAlreadyCreatedException
from domain.values import Title, Money


@pytest.mark.asyncio
@pytest.mark.accounts
@pytest.mark.integration
class TestAccountService:

    async def test_create(
        self,
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
                balance=float(test_account.balance.as_generic_type()),
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

    async def test_name_taken_error(
        self,
        test_account,
        test_account_repo,
        test_account_publisher: AsyncMock,
        test_account_service,
    ):
        new_account = copy(test_account)
        new_account.name = Title("Новый счет")

        await test_account_repo.save(new_account)

        with pytest.raises(AccountAlreadyCreatedException):
            await test_account_service.create_account(
                command=CreateAccountCommand(
                    user_id=test_account.user_id.as_generic_type(),
                    name="Новый счет",
                    balance=float(test_account.balance.as_generic_type()),
                    account_type=test_account.type,
                    currency=test_account.currency,
                )
            )

    async def test_update(
        self,
        faker: Faker,
        test_account,
        test_account_repo,
        test_account_publisher: AsyncMock,
        test_account_service,
    ):
        await test_account_repo.save(test_account)

        balance = float(test_account.balance.as_generic_type())
        new_balance = Money(balance + faker.pyfloat(min_value=balance))

        await test_account_service.update_balance(
            command=UpdateAccountBalanceCommand(
                user_id=test_account.user_id.as_generic_type(),
                account_id=test_account.id.as_generic_type(),
                new_balance=float(new_balance.as_generic_type()),
            )
        )

        test_account_publisher.publish.assert_awaited_once()

        exists_account = await test_account_repo.get_by_id(
            user_id=test_account.user_id.as_generic_type(),
            account_id=test_account.id.as_generic_type(),
        )

        assert exists_account.balance == new_balance
