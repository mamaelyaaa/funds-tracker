import logging
from typing import Annotated

from fastapi import Depends

from domain.users.entity import User
from infra.publishers.accounts import AccountEventPublisherDep
from infra.repositories.accounts import AccountRepositoryDep
from .commands import (
    CreateAccountCommand,
    GetAccountCommand,
    UpdateAccountBalanceCommand,
)
from .dto import AccountDTO
from .entity import Account
from .exceptions import (
    AccountNotFoundException,
    TooManyAccountsForUserException,
    AccountAlreadyCreatedException,
)
from .protocols import AccountRepositoryProtocol, AccountEventPublisherProtocol

logger = logging.getLogger(__name__)


class AccountCRUDService:

    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        account_publisher: AccountEventPublisherProtocol,
    ):
        self._repository = account_repo
        self._publisher = account_publisher

    async def create_account(self, command: CreateAccountCommand) -> Account:
        """
        Создаем новый счет

        - Если счёт для текущего пользователя уже существует - ошибка
        - Если превышен лимит активных счётов пользователя - ошибка
        """

        # Проверка на существование счёта с таким названием
        check = await self._repository.is_name_taken(
            user_id=command.user_id, name=command.name
        )
        if check:
            logger.warning(
                f"Ошибка создания нового счёта для пользователя #{command.user_id[:8]}"
            )
            raise AccountAlreadyCreatedException

        # Проверка на лимит активных счетов пользователя
        count = await self._repository.count_by_user_id(command.user_id)
        if count >= User.MAX_ACCOUNTS:
            logger.warning(
                f"Пользователь #%s превысил лимит активных счётов", command.user_id[:8]
            )
            raise TooManyAccountsForUserException

        new_account = Account.create(
            user_id=command.user_id,
            name=command.name,
            balance=command.balance,
            account_type=command.account_type,
            currency=command.currency,
        )
        acc_id = await self._repository.save(new_account)

        for event in new_account.events:
            await self._publisher.publish(event)

        logger.info("Новый счёт #%s создан", acc_id)

        return new_account

    async def find_account_by_id(self, command: GetAccountCommand) -> Account:
        if not (
            account := await self._repository.get_by_id(
                account_id=command.account_id,
                user_id=command.user_id,
            )
        ):
            logger.warning("Счёт #%s не найден", command.account_id)
            raise AccountNotFoundException

        logger.info(f"Счёт #{command.account_id} получен")
        return account

    async def find_accounts_by_user_id(self, user_id: str) -> list[Account]:
        accounts = await self._repository.get_by_user_id(user_id)
        return accounts

    async def delete_account(self, command: GetAccountCommand) -> None:
        account = await self.find_account_by_id(command=command)
        await self._repository.delete(
            account_id=account.id.as_generic_type(),
            user_id=account.user_id.as_generic_type(),
        )
        logger.info("Счёт #%s был удален", account.id.as_generic_type())
        return


class AccountService(AccountCRUDService):
    """Сервис управления счетами пользователей"""

    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        account_publisher: AccountEventPublisherProtocol,
    ):
        super().__init__(account_repo, account_publisher)

    async def update_balance(self, command: UpdateAccountBalanceCommand) -> None:
        """Обновляем баланс счета"""

        account = await self.find_account_by_id(
            command=GetAccountCommand(
                account_id=command.account_id, user_id=command.user_id
            )
        )

        if command.new_balance == account.balance:
            logger.info("Баланс счета #%s не изменен", account.id.as_generic_type())
            return

        account.update_balance(command.new_balance)

        await self._repository.update(
            account_id=command.account_id,
            user_id=command.user_id,
            upd_data=AccountDTO.from_entity_to_dict(
                account, excludes=["id", "user_id"]
            ),
        )
        logger.info("Баланс счета #%s обновлен", account.id.as_generic_type())

        if len(account.events) > 1:
            logger.error("Лишние события в доменной модели")

        for event in account.events:
            await self._publisher.publish(event)

        account.events.clear()
        return

    # async def rename_account(self, command: UpdateAccountNameCommand) -> None:
    #     account = await self.find_account_by_id(command.account_id)
    #     account.rename_account(Title(command.new_name))
    #
    #     await self._repository.save(account)
    #     logger.info("Название счета #%s обновлено", account.id.value)
    #     return


def get_account_service(
    acc_repo: AccountRepositoryDep,
    acc_publisher: AccountEventPublisherDep,
) -> AccountService:
    return AccountService(account_repo=acc_repo, account_publisher=acc_publisher)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
