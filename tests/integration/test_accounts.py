# from unittest.mock import AsyncMock
#
# import pytest
# from faker.proxy import Faker
#
# from domain.accounts.comands import CreateAccountCommand
# from domain.accounts.entity import Account
# from domain.accounts.events import AccountCreatedEvent
# from domain.accounts.exceptions import (
#     AccountAlreadyCreatedException,
#     TooManyAccountsForUserException,
#     AccountNotFoundException,
# )
# from domain.accounts.publisher import AccountEventPublisherProtocol
# from domain.accounts.service import AccountService
# from domain.accounts.values import Title, AccountCurrency, AccountType, AccountId
# from domain.users.entity import User
# from domain.users.values import UserId
# from infra.publishers.accounts import AccountTaskiqPublisher
# from infra.repositories.accounts import InMemoryAccountRepository
#
#
# @pytest.fixture
# def mock_account(faker: Faker) -> Account:
#     return Account.create(
#         user_id=UserId("user-123"),
#         name=Title("Новый счёт"),
#         currency=AccountCurrency.RUB,
#         account_type=AccountType.CARD,
#         balance=faker.pyfloat(positive=True),
#     )
#
#
# @pytest.fixture
# def mock_acc_repo(mock_account):
#     repo = InMemoryAccountRepository()
#     return repo
#
#
# @pytest.fixture
# def mock_acc_publisher(mock_account) -> AccountEventPublisherProtocol:
#     publisher = AccountTaskiqPublisher()
#     publisher.publish = AsyncMock()
#     return publisher
#
#
# @pytest.fixture
# def mock_acc_service(mock_acc_repo, mock_acc_publisher) -> AccountService:
#     return AccountService(
#         account_repo=mock_acc_repo,
#         account_publisher=mock_acc_publisher,
#     )
#
#
# async def create_account(mock_acc_service, mock_account) -> Account:
#     account = await mock_acc_service.create_account(
#         command=CreateAccountCommand(
#             user_id=mock_account.user_id.value,
#             account_type=mock_account.type,
#             balance=mock_account.balance,
#             name=mock_account.name.value,
#             currency=mock_account.currency,
#         )
#     )
#     return account
#
#
# @pytest.mark.asyncio
# @pytest.mark.integration
# class TestAccountServiceCreate:
#
#     async def test_service_account_creation(
#         self,
#         mock_acc_service,
#         mock_account,
#         mock_acc_repo,
#         mock_acc_publisher: AsyncMock,
#     ):
#         """Тест на успешное создание счёта сервисом"""
#
#         account = await create_account(mock_acc_service, mock_account)
#
#         # Проверка репозитория
#         saved_account = await mock_acc_repo.get_by_id(account_id=account.id)
#
#         assert saved_account.id == account.id
#         assert saved_account.balance == account.balance
#         assert saved_account.created_at == account.created_at
#
#         # Проверка publisher'а
#         mock_acc_publisher.publish.assert_awaited_once()
#
#     async def test_service_account_name_already_taken(
#         self,
#         mock_acc_service,
#         mock_account,
#         mock_acc_repo,
#     ):
#         """Тест счёт с таким названием уже существует"""
#         await mock_acc_repo.save(mock_account)
#
#         with pytest.raises(AccountAlreadyCreatedException):
#             await create_account(mock_acc_service, mock_account)
#
#         assert len(mock_acc_repo._storage) == 1
#
#     async def test_service_account_creation_limit_reached(
#         self,
#         mock_acc_service,
#         mock_account,
#         mock_acc_repo: AsyncMock,
#     ):
#         """Тест превышен лимит создания счётов"""
#
#         mock_acc_repo.count_by_user_id = AsyncMock(returnas_generic_type()=User.MAX_ACCOUNTS)
#
#         with pytest.raises(TooManyAccountsForUserException):
#             await create_account(mock_acc_service, mock_account)
#
#
# @pytest.mark.asyncio
# @pytest.mark.integration
# class TestAccountServiceDeletion:
#
#     @staticmethod
#     async def delete_account(mock_acc_service: AccountService, account_id: str) -> None:
#         await mock_acc_service.delete_account(account_id=account_id)
#
#     async def test_service_account_delete(
#         self,
#         mock_acc_service,
#         mock_account,
#         mock_acc_repo: AsyncMock,
#     ):
#         mock_acc_repo.delete = AsyncMock(returnas_generic_type()=mock_account.id)
#
#         await self.delete_account(mock_acc_service, account_id=mock_account.id.value)
#
#         mock_acc_repo.get_by_id.assert_awaited_once()
#         mock_acc_repo.delete.assert_awaited_once()
#
#         deleted_account_id: AccountId = mock_acc_repo.delete.call_args[0][0]
#         assert deleted_account_id == mock_account.id
#
#     async def test_service_account_for_delete_is_not_found(
#         self,
#         mock_acc_service,
#         mock_account,
#         mock_acc_repo: AsyncMock,
#     ):
#         mock_acc_repo.delete = AsyncMock(returnas_generic_type()=None)
#         mock_acc_repo.get_by_id = AsyncMock(returnas_generic_type()=None)
#
#         with pytest.raises(AccountNotFoundException):
#             await self.delete_account(
#                 mock_acc_service,
#                 account_id=mock_account.id.value,
#             )
