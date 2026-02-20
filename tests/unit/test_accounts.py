from datetime import datetime

import pytest
from faker import Faker

from domain.accounts.entity import Account
from domain.accounts.exceptions import (
    TooLargeTitleException,
    InvalidLettersTitleException,
    InvalidInitBalanceException,
)
from domain.accounts.values import Title, AccountCurrency, AccountType


@pytest.mark.unit
@pytest.mark.accounts
class TestAccountDomain:

    def test_domain_creation_success(self, test_account):
        """Тест создания счёта"""

        assert test_account.created_at.date() == datetime.now().date()
        assert test_account.balance > 0
        assert test_account.type == "Card"
        assert test_account.currency == "RUB"

    def test_invalid_initial_balance(self, faker: Faker):
        """Тест создания счёта с невалидным балансом"""

        with pytest.raises(InvalidInitBalanceException):
            Account.create(
                user_id="user-123",
                name=faker.word(),
                currency=AccountCurrency.RUB,
                account_type=AccountType.CARD,
                balance=faker.pyfloat(positive=False),
            )

    def test_update_balance_success(self, test_account, faker: Faker):
        """Тест на обновление баланса счёта"""

        assert len(test_account.events) == 1

        test_account.update_balance(new_balance=5000)
        assert test_account.balance == 5000
        assert len(test_account.events) == 2


@pytest.mark.unit
class TestAccountValueObjects:

    def test_title_too_large_exception(self, faker: Faker):
        with pytest.raises(TooLargeTitleException):
            Title(faker.text(max_nb_chars=100))

    def test_title_invalid_letters(self, faker: Faker):
        with pytest.raises(InvalidLettersTitleException):
            Title(faker.phone_number())
