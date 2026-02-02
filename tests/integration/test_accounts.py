from unittest.mock import AsyncMock

import pytest

from domain.accounts.comands import CreateAccountCommand
from domain.accounts.entity import Account
from domain.accounts.events import AccountCreatedEvent
from domain.accounts.exceptions import (
    AccountAlreadyCreatedException,
    TooManyAccountsForUserException,
    AccountNotFoundException,
)
from domain.accounts.service import AccountService
from domain.accounts.values import Title, AccountCurrency, AccountType, AccountId
from domain.users.entity import User
from domain.users.values import UserId
from infra.publishers.accounts import AccountTaskiqPublisher
from infra.repositories.accounts import InMemoryAccountRepository


@pytest.fixture
def mock_account() -> Account:
    return Account.create(
        user_id=UserId("user-123"),
        name=Title("Новый счёт"),
        currency=AccountCurrency.RUB,
        account_type=AccountType.CARD,
        balance=150,
    )


@pytest.fixture
def mock_acc_repo(mock_account):
    repo = InMemoryAccountRepository()

    repo.save = AsyncMock(return_value=mock_account.id)
    repo.get_by_id = AsyncMock(return_value=mock_account)

    return repo


@pytest.fixture
def mock_acc_publisher(mock_account):
    publisher = AccountTaskiqPublisher()
    publisher.publish = AsyncMock()
    return publisher


@pytest.fixture
def mock_acc_service(mock_acc_repo, mock_acc_publisher):
    return AccountService(
        account_repo=mock_acc_repo,
        account_publisher=mock_acc_publisher,
    )


@pytest.mark.asyncio
@pytest.mark.integration
class TestAccountServiceCreation:

    @staticmethod
    async def create_account(mock_acc_service, mock_account) -> Account:
        account = await mock_acc_service.create_account(
            command=CreateAccountCommand(
                user_id=mock_account.user_id.value,
                account_type=mock_account.type,
                balance=mock_account.balance,
                name=mock_account.name.value,
                currency=mock_account.currency,
            )
        )
        return account

    async def test_service_account_creation(
        self,
        mock_acc_service,
        mock_account,
        mock_acc_repo: AsyncMock,
        mock_acc_publisher: AsyncMock,
    ):
        account = await self.create_account(mock_acc_service, mock_account)

        # Проверка репозитория
        mock_acc_repo.save.assert_awaited_once()
        saved_account = mock_acc_repo.save.call_args[0][0]

        assert isinstance(saved_account, Account)
        assert account.id == saved_account.id
        assert account.user_id == saved_account.user_id
        assert account.name.value == saved_account.name.value

        # Проверка publisher'а
        mock_acc_publisher.publish.assert_called_once()
        publish_event = mock_acc_publisher.publish.call_args[0][0]

        assert isinstance(publish_event, AccountCreatedEvent)
        assert publish_event.account_id == account.id
        assert publish_event.new_balance == account.balance

    async def test_service_account_name_already_taken(
        self,
        mock_acc_service,
        mock_account,
        mock_acc_repo: AsyncMock,
    ):
        mock_acc_repo.is_name_taken = AsyncMock(return_value=True)

        with pytest.raises(AccountAlreadyCreatedException):
            await self.create_account(mock_acc_service, mock_account)

    async def test_service_account_creation_limit_reached(
        self,
        mock_acc_service,
        mock_account,
        mock_acc_repo: AsyncMock,
    ):
        mock_acc_repo.count_by_user_id = AsyncMock(return_value=User.MAX_ACCOUNTS)

        with pytest.raises(TooManyAccountsForUserException):
            await self.create_account(mock_acc_service, mock_account)


@pytest.mark.asyncio
@pytest.mark.integration
class TestAccountServiceDeletion:

    @staticmethod
    async def delete_account(mock_acc_service: AccountService, account_id: str) -> None:
        await mock_acc_service.delete_account(account_id=account_id)

    async def test_service_account_delete(
        self,
        mock_acc_service,
        mock_account,
        mock_acc_repo: AsyncMock,
    ):
        mock_acc_repo.delete = AsyncMock(return_value=mock_account.id)

        await self.delete_account(mock_acc_service, account_id=mock_account.id.value)

        mock_acc_repo.get_by_id.assert_awaited_once()
        mock_acc_repo.delete.assert_awaited_once()

        deleted_account_id: AccountId = mock_acc_repo.delete.call_args[0][0]
        assert deleted_account_id == mock_account.id

    async def test_service_account_for_delete_is_not_found(
        self,
        mock_acc_service,
        mock_account,
        mock_acc_repo: AsyncMock,
    ):
        mock_acc_repo.delete = AsyncMock(return_value=None)
        mock_acc_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(AccountNotFoundException):
            await self.delete_account(
                mock_acc_service,
                account_id=mock_account.id.value,
            )
