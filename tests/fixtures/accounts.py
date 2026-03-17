from unittest.mock import AsyncMock

import pytest
from faker import Faker

from api.v1.dependencies.accounts import get_account_service
from domain.accounts.entity import Account
from domain.accounts.service import AccountService
from domain.accounts.values import AccountCurrency, AccountType
from domain.values import Money, Title


@pytest.fixture
def test_account(saved_user, faker: Faker) -> Account:
    """Тестовый счёт"""

    return Account(
        user_id=saved_user.id,
        name=Title(faker.word()),
        currency=AccountCurrency.RUB,
        type=AccountType.CARD,
        balance=Money(faker.pyfloat(positive=True)),
    )


@pytest.fixture
def test_account_service(test_session) -> AccountService:
    """Тестовый сервис счётов"""

    account_service: AccountService = get_account_service(test_session)
    return account_service


@pytest.fixture
async def saved_account(test_account, test_account_service) -> Account:
    """Тестовый сохраненный в БД счёт"""

    await test_account_service.repository.save(test_account)
    return test_account
