import pytest

from accounts.cache import AccountCacheProtocol
from accounts.comands import CreateAccountCommand
from accounts.exceptions import (
    InvalidInitBalanceException,
    AccountAlreadyCreatedException,
)
from accounts.publisher import AccountEventPublisherProtocol
from accounts.repository import AccountRepositoryProtocol
from accounts.service import AccountService
from accounts.values import AccountCurrency, AccountType
from infra.cache.accounts import InMemoryAccountCache
from infra.publishers.accounts import AccountTaskiqPublisher
from infra.repositories.accounts import InMemoryAccountRepository


@pytest.fixture
def account_repository() -> AccountRepositoryProtocol:
    return InMemoryAccountRepository()


@pytest.fixture
def account_publisher() -> AccountEventPublisherProtocol:
    return AccountTaskiqPublisher()


@pytest.fixture
def account_cache() -> AccountCacheProtocol:
    return InMemoryAccountCache()


@pytest.fixture
def account_service(
    account_repository, account_publisher, account_cache
) -> AccountService:
    return AccountService(account_repository, account_publisher, account_cache)


@pytest.mark.asyncio
class TestAccountCreation:

    async def test_service_success(
        self, account_service, account_repository, account_cache
    ):
        account_id = await account_service.create_account(
            command=CreateAccountCommand(
                user_id="123",
                name="Подушка безопасности",
                currency=AccountCurrency.RUB,
                account_type=AccountType.CARD,
                balance=0,
            )
        )

        assert (account := await account_repository.get_by_id(account_id)) is not None
        assert await account_cache.get(account_id) == account
        assert account.user_id.value == "123"
        assert account.balance == 0
        assert account.currency == AccountCurrency.RUB
        assert account.type == AccountType.CARD
        assert account.name.value == "Подушка безопасности"

    async def test_service_negative_balance(self, account_service):
        """Ошибка невалидного изначального баланса счёта при создании"""

        with pytest.raises(InvalidInitBalanceException):
            await account_service.create_account(
                command=CreateAccountCommand(
                    user_id="123",
                    name="Долги",
                    currency=AccountCurrency.RUB,
                    account_type=AccountType.CARD,
                    balance=-1000,  # ❌ Отрицательный баланс
                )
            )

    async def test_service_duplicate_names(self, account_service):
        """Ошибка создания счёта с таким же названием"""

        same_name = "Банк"
        user_id = "123"

        await account_service.create_account(
            command=CreateAccountCommand(
                user_id=user_id,
                name=same_name,
                currency=AccountCurrency.RUB,
                account_type=AccountType.CARD,
                balance=1000,
            )
        )

        with pytest.raises(AccountAlreadyCreatedException):
            await account_service.create_account(
                command=CreateAccountCommand(
                    user_id=user_id,
                    name=same_name,
                    currency=AccountCurrency.USD,
                    account_type=AccountType.CARD,
                    balance=0,
                )
            )
