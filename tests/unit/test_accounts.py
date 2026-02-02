from datetime import datetime
from typing import cast

import pytest
from faker import Faker

from domain.accounts.entity import Account
from domain.accounts.events import BalanceUpdatedEvent, AccountCreatedEvent
from domain.accounts.exceptions import (
    TooLargeTitleException,
    InvalidLettersTitleException,
    InvalidInitBalanceException,
)
from domain.accounts.values import Title, AccountCurrency, AccountType
from domain.users.values import UserId


@pytest.mark.unit
class TestAccountDomain:

    def test_domain_creation_success(self, faker: Faker):
        """Тест создания счёта"""

        account = Account.create(
            user_id=UserId("user-123"),
            name=Title(faker.word()),
            currency=AccountCurrency.RUB,
            account_type=AccountType.CARD,
            balance=150,
        )

        assert account.user_id.value == "user-123"
        assert account.created_at.date() == datetime.now().date()
        assert account.balance == 150
        assert account.type == "Card"
        assert account.currency == "RUB"

    def test_invalid_initial_balance(self, faker: Faker):
        """Тест создания счёта с невалидным балансом"""

        with pytest.raises(InvalidInitBalanceException):
            Account.create(
                user_id=UserId("user-123"),
                name=Title(faker.word()),
                currency=AccountCurrency.RUB,
                account_type=AccountType.CARD,
                balance=-100,
            )

    def test_update_balance_success(self, faker: Faker):
        """Тест на обновление баланса счёта"""

        account = Account.create(
            user_id=UserId("user-123"),
            name=Title(faker.word()),
            currency=AccountCurrency.USD,
            account_type=AccountType.CASH,
            balance=30,
        )
        assert len(account.events) == 1
        event1 = cast(AccountCreatedEvent, account.events[0])

        account.update_balance(new_balance=5000)
        assert account.balance == 5000

        assert len(account.events) == 2
        event2 = cast(BalanceUpdatedEvent, account.events[1])

        assert event1.new_balance == 30
        assert event2.new_balance == 5000


@pytest.mark.unit
class TestAccountValueObjects:

    def test_title_too_large_exception(self, faker: Faker):
        with pytest.raises(TooLargeTitleException):
            Title(faker.text(max_nb_chars=100))

    def test_title_invalid_letters(self, faker: Faker):
        with pytest.raises(InvalidLettersTitleException):
            Title(faker.phone_number())
