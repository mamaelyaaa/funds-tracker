from unittest.mock import AsyncMock

import pytest
from faker.proxy import Faker

from domain.accounts.commands import CreateAccountCommand, UpdateAccountBalanceCommand
from domain.accounts.entities import Account, AccountType, AccountCurrency
from domain.accounts.exceptions import AccountAlreadyCreatedException
from domain.values import Title, Money


@pytest.mark.asyncio
@pytest.mark.accounts
@pytest.mark.integration
class TestAccountService:

    async def test_create(self, test_account, test_account_service):
        """Тест счёт успешно создан"""

        test_account_service.publisher = AsyncMock()

        account = await test_account_service.create_account(
            command=CreateAccountCommand(
                user_id=test_account.user_id,
                name=test_account.name,
                balance=float(test_account.balance),
                account_type=test_account.type,
                currency=test_account.currency,
            )
        )

        exists_acc = await test_account_service.repository.find_one(
            user_id=account.user_id,
            id=account.id,
        )

        assert account.id == exists_acc.id
        assert account.balance == exists_acc.balance
        assert account.currency == exists_acc.currency
        assert account.type == exists_acc.type

        test_account_service.publisher.publish.assert_awaited_once()

    async def test_name_taken_error(self, saved_user, test_account_service):
        new_account = Account(
            user_id=saved_user.id,
            name=Title("Новый счет"),
            currency=AccountCurrency.RUB,
            type=AccountType.CARD,
            balance=Money(0),
        )
        await test_account_service.repository.save(new_account)

        with pytest.raises(AccountAlreadyCreatedException):
            await test_account_service.create_account(
                command=CreateAccountCommand(
                    user_id=new_account.user_id,
                    name="Новый счет",
                    balance=float(new_account.balance),
                    account_type=new_account.type,
                    currency=new_account.currency,
                )
            )

    async def test_update(self, faker: Faker, saved_account, test_account_service):
        test_account_service.publisher.publish = AsyncMock()

        balance = float(saved_account.balance)
        new_balance = Money(balance + faker.pyfloat(min_value=balance))

        await test_account_service.update_balance(
            command=UpdateAccountBalanceCommand(
                user_id=saved_account.user_id,
                account_id=saved_account.id,
                new_balance=float(new_balance),
            )
        )

        assert test_account_service.publisher.publish.await_count == 1

        exists_account = await test_account_service.repository.find_one(
            user_id=saved_account.user_id,
            id=saved_account.id,
        )

        assert exists_account.balance == new_balance

    async def test_update_same_balance(self, saved_account, test_account_service):
        test_account_service.publisher.publish = AsyncMock()

        await test_account_service.update_balance(
            command=UpdateAccountBalanceCommand(
                user_id=saved_account.user_id,
                account_id=saved_account.id,
                new_balance=float(saved_account.balance),
            )
        )

        test_account_service.publisher.publish.assert_not_awaited()

        exists_account = await test_account_service.repository.find_one(
            id=saved_account.id,
            user_id=saved_account.user_id,
        )

        assert exists_account.balance == saved_account.balance
