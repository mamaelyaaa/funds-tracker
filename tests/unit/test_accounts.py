from datetime import datetime
from typing import cast

import pytest
from faker import Faker

from accounts.entities import Account
from accounts.events import BalanceUpdatedEvent
from accounts.exceptions import (
    TooLargeTitleException,
    InvalidLettersTitleException,
    InvalidInitBalanceException,
)
from accounts.values import Title, AccountCurrency, AccountType, AccountId
from users.values import UserId


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
        assert len(account.name.value) < account.name.MAX_LEN

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

        account.update_balance(new_balance=5000)

        assert account.balance == 5000
        assert len(account.events) > 0
        assert account.user_id.value == "user-123"
        assert account.type == "Cash"
        assert account.currency == "USD"

    def test_update_balance_generates_event(self, faker: Faker):
        """Тест на генерацию события после обновления счёта"""

        account = Account.create(
            user_id=UserId("user-123"),
            name=Title(faker.word()),
            currency=AccountCurrency.RUB,
            account_type=AccountType.CARD,
            balance=150,
        )
        account.update_balance(new_balance=200)

        assert len(account.events) == 1
        event = cast(BalanceUpdatedEvent, account.events[0])

        assert event.old_balance == 150
        assert event.new_balance == 200
        assert event.account_id == account.id
        assert event.user_id == account.user_id


@pytest.mark.unit
class TestAccountValueObjects:

    def test_title_too_large_exception(self, faker: Faker):
        with pytest.raises(TooLargeTitleException):
            Title(faker.text(max_nb_chars=100))

    def test_title_invalid_letters(self, faker: Faker):
        with pytest.raises(InvalidLettersTitleException):
            Title(faker.phone_number())

    def test_account_id(self):
        aid1 = AccountId("acc-1")
        aid2 = AccountId("acc-1")

        assert aid1 == aid2
        assert hash(aid1) == hash(aid2)
