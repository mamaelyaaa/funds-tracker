from datetime import timezone, datetime, timedelta

import pytest
from faker.proxy import Faker

from domain.accounts.commands import CreateAccountCommand, UpdateAccountBalanceCommand
from domain.funds.entity import Fund
from domain.funds.values import FundStatus
from domain.values import Money


@pytest.mark.asyncio
@pytest.mark.funds
@pytest.mark.integration
class TestFundService:

    async def test_creation_success(
        self, faker: Faker, test_account, test_account_service, test_fund_service
    ):
        """Проверка успешного создания остатка"""

        # Создание остатка происходит за счёт создания нового счёта, либо обновления баланса (если уже есть
        # закрытые остатки)

        assert (
            await test_account_service.repository.count_by_user_id(
                test_account.user_id.as_generic_type()
            )
            == 0
        )

        account = await test_account_service.create_account(
            command=CreateAccountCommand(
                user_id=test_account.user_id.as_generic_type(),
                balance=(new_balance := faker.pyfloat(positive=True)),
                name=test_account.name.as_generic_type(),
                account_type=test_account.type,
                currency=test_account.currency,
            )
        )

        fund = await test_fund_service._fund_repo.get_by_user_id(
            user_id=account.user_id.as_generic_type()
        )

        assert fund.user_id == account.user_id
        assert fund.total_amount == Money(new_balance)
        assert fund.start_date == account.created_at
        assert fund.end_date > fund.start_date
        assert fund.status == FundStatus.OPEN

    async def test_creation_success_after_exists(
        self,
        test_fund_service,
        test_fund,
        test_account_service,
        test_account,
        faker: Faker,
    ):
        """Проверка успешного создания остатка после имеющихся закрытых"""

        test_closed_fund = Fund(
            user_id=test_account.user_id,
            total_amount=Money(faker.pyfloat(positive=True)),
            status=FundStatus.CLOSED,
            start_date=datetime(year=2026, month=3, day=1, tzinfo=timezone.utc),
            end_date=datetime(year=2026, month=3, day=2, tzinfo=timezone.utc),
        )

        await test_fund_service._fund_repo.save(test_closed_fund)
        assert (
            await test_fund_service._fund_repo.get_last_closed(
                user_id=test_closed_fund.user_id.as_generic_type()
            )
            is not None
        )

        account = await test_account_service.create_account(
            command=CreateAccountCommand(
                user_id=test_account.user_id.as_generic_type(),
                balance=200,
                name=test_account.name.as_generic_type(),
                account_type=test_account.type,
                currency=test_account.currency,
            )
        )

        assert (
            last_closed_fund := await test_fund_service._fund_repo.get_last_closed(
                user_id=test_closed_fund.user_id.as_generic_type()
            )
        ) is not None

        fund = await test_fund_service._fund_repo.get_last_opened(
            user_id=account.user_id.as_generic_type()
        )

        assert fund.user_id == account.user_id
        assert fund.total_amount == Money(200)
        assert fund.start_date == last_closed_fund.end_date + timedelta(days=1)
        assert fund.end_date > fund.start_date
        assert fund.status == FundStatus.OPEN

    async def test_creation_success_after_exists_with_update(
        self, faker: Faker, saved_account, test_fund_service, test_account_service
    ):
        """Проверка успешного создания после имеющихся закрытых с помощью обновления существующего баланса"""
        test_closed_fund = Fund(
            user_id=saved_account.user_id,
            total_amount=Money(200),
            status=FundStatus.CLOSED,
            start_date=datetime(year=2026, month=3, day=1, tzinfo=timezone.utc),
            end_date=datetime.now(timezone.utc) - timedelta(days=2),
        )
        await test_fund_service._fund_repo.save(test_closed_fund)
        assert (
            await test_fund_service._fund_repo.get_last_closed(
                user_id=saved_account.user_id.as_generic_type()
            )
            is not None
        )

        new_balance = faker.pyfloat(positive=True)
        assert Money(new_balance) != saved_account.balance

        await test_account_service.update_balance(
            command=UpdateAccountBalanceCommand(
                user_id=saved_account.user_id.as_generic_type(),
                account_id=saved_account.id.as_generic_type(),
                new_balance=new_balance,
                is_monthly_closing=True,
            )
        )

        new_fund = await test_fund_service._fund_repo.get_last_opened(
            user_id=saved_account.user_id.as_generic_type()
        )
        assert new_fund is not None

        assert new_fund.total_amount == Money(new_balance)
        assert new_fund.start_date == test_closed_fund.end_date + timedelta(days=1)
        assert new_fund.status == FundStatus.OPEN

    async def test_update_exists_success(self):
        """Проверка успешного обновления существующего остатка"""
        pass

    async def test_input_reserves_validation_success(self):
        """Проверка успешной валидации входных резервов"""
        pass

    async def test_distribute_success(self):
        """Проверка успешного распределения остатка"""
        pass

    async def test_distribute_errors(self):
        """Проверка возможных ошибок при распределении остатка"""
        pass

    async def test_close_fund_success(self):
        """Успешная обработка и распределение накопленного остатка за период"""
        pass
