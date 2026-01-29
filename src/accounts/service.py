import logging

from infra.publishers.accounts import AccountEventPublisherDep
from infra.repositories.accounts import AccountRepositoryDep
from users.domain import User
from users.values import UserId
from .domain import (
    Account,
    AccountType,
    AccountId,
    AccountCurrency,
)
from .exceptions import (
    AccountNotFoundException,
    TooManyAccountsForUserException,
    AccountAlreadyCreatedException,
)
from .publisher import AccountEventPublisherProtocol
from .repository import AccountRepositoryProtocol
from .values import Title

logger = logging.getLogger(__name__)


class AccountCRUDService:

    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        account_publisher: AccountEventPublisherProtocol,
    ):
        self._repository = account_repo
        self._publisher = account_publisher

    async def create_account(
        self,
        user_id: str,
        name: str,
        initial_balance: float,
        account_type: AccountType,
        currency: AccountCurrency,
    ) -> AccountId:
        """Создаем новый счет"""

        user_id_obj = UserId(user_id)
        acc_name = Title(name)

        check = await self._repository.is_name_taken(user_id_obj, acc_name)
        if check:
            logger.warning(
                f"Ошибка создания нового счёта для пользователя #{user_id_obj.short}"
            )
            raise AccountAlreadyCreatedException

        count = await self._repository.count_by_user_id(user_id_obj)
        if count >= User.MAX_ACCOUNTS:
            logger.warning(
                f"Пользователь #%s превысил лимит активных счётов", user_id_obj.short
            )
            raise TooManyAccountsForUserException

        new_account = Account.create(
            user_id=user_id_obj,
            name=acc_name,
            balance=initial_balance,
            account_type=account_type,
            currency=currency,
        )
        acc_id = await self._repository.save(new_account)
        logger.info("Новый счёт #%s создан", acc_id.value)
        return acc_id

    async def find_account_by_id(self, account_id: str) -> Account:
        account_id_obj = AccountId(account_id)
        if not (account := await self._repository.get_by_id(account_id_obj)):
            logger.warning("Счёт #%s не найден", account_id_obj.value)
            raise AccountNotFoundException
        return account

    async def find_accounts_by_user_id(self, user_id: str) -> list[Account]:
        user_id_obj = UserId(user_id)
        accounts = await self._repository.get_by_user_id(user_id_obj)
        return accounts

    async def delete_account(self, account_id: str) -> None:
        account = await self.find_account_by_id(account_id)

        await self._repository.delete(account.id)
        logger.info("Счёт #%s был удален", account.id.value)
        return


class AccountService(AccountCRUDService):
    """Сервис управления счетами пользователей"""

    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        account_publisher: AccountEventPublisherProtocol,
    ):
        super().__init__(account_repo, account_publisher)

    async def set_new_balance(self, account_id: str, actual_balance: float) -> None:
        """Обновляем баланс счета"""

        account = await self.find_account_by_id(account_id)

        if actual_balance == account.balance:
            logger.info("Баланс счета #%s не изменен", account.id.value)
            return

        account.update_balance(actual_balance)

        await self._repository.update(AccountId(account_id), account)
        logger.info("Баланс счета #%s обновлен", account.id.value)

        for event in account.events:
            await self._publisher.publish(event)

        account.events.clear()
        return

    async def rename_account(self, account_id: str, new_name: str) -> None:
        account = await self.find_account_by_id(account_id)
        account.rename_account(Title(new_name))

        await self._repository.save(account)
        logger.info("Название счета #%s обновлено", account.id.value)
        return


def get_account_service(
    acc_repo: AccountRepositoryDep,
    acc_publisher: AccountEventPublisherDep,
) -> AccountService:
    return AccountService(
        account_repo=acc_repo,
        account_publisher=acc_publisher,
    )
