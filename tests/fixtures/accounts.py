from unittest.mock import AsyncMock

import pytest
from faker import Faker

from domain.accounts.entity import Account
from domain.accounts.protocols import (
    AccountRepositoryProtocol,
    AccountEventPublisherProtocol,
)
from domain.accounts.service import AccountService
from domain.accounts.values import AccountCurrency, AccountType
from infra.publishers.accounts import AccountTaskiqPublisher
from infra.repositories.accounts import InMemoryAccountRepository


@pytest.fixture
def test_account(faker: Faker) -> Account:
    return Account.create(
        user_id="user-123",
        name=faker.word(),
        currency=AccountCurrency.RUB,
        account_type=AccountType.CARD,
        balance=faker.pyfloat(positive=True),
    )


@pytest.fixture
def test_account_repo() -> AccountRepositoryProtocol:
    return InMemoryAccountRepository()


@pytest.fixture
def test_account_publisher() -> AccountEventPublisherProtocol:
    publisher = AccountTaskiqPublisher()
    publisher.publish = AsyncMock()
    return publisher


@pytest.fixture
def test_account_service(test_account_repo, test_account_publisher) -> AccountService:
    return AccountService(
        account_repo=test_account_repo,
        account_publisher=test_account_publisher,
    )
