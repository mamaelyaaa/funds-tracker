from datetime import datetime

import pytest
from faker import Faker

from domain.accounts.entity import Account
from domain.accounts.values import AccountType, AccountCurrency
from domain.exceptions import (
    InvalidBalanceException,
    TooLargeTitleException,
    InvalidLettersTitleException,
)
from domain.users.values import UserId
from domain.values import Money, Title


@pytest.mark.unit
@pytest.mark.accounts
class TestAccountDomain:

    def test_domain_creation_success(self, test_account):
        """Тест создания счёта"""

        assert test_account.created_at.date() == datetime.now().date()
        assert test_account.balance.as_generic_type() > 0
        assert test_account.type == "Card"
        assert test_account.currency == "RUB"

    def test_invalid_initial_balance(self, faker: Faker):
        """Тест создания счёта с невалидным балансом"""

        with pytest.raises(InvalidBalanceException):
            Account.create(
                user_id=UserId("user-123"),
                name=Title(faker.word()),
                currency=AccountCurrency.RUB,
                account_type=AccountType.CARD,
                balance=Money(faker.pyfloat(positive=False)),
            )

    def test_update_balance_success(self, test_account):
        """Тест на обновление баланса счёта"""

        test_account.update_balance(
            new_balance=Money(5000.3454),
            is_monthly_closing=True,
        )
        assert test_account.balance == Money(5000.35)
        assert test_account.updated_at > test_account.created_at
        assert len(test_account.events) > 0


@pytest.mark.unit
class TestAccountValueObjects:

    def test_title_too_large_exception(self, faker: Faker):
        with pytest.raises(TooLargeTitleException):
            Title(faker.text(max_nb_chars=100))

    def test_title_invalid_letters(self, faker: Faker):
        with pytest.raises(InvalidLettersTitleException):
            Title(faker.phone_number())
