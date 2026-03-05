import logging

from domain.users.entity import User
from domain.users.values import UserId
from domain.values import Money, Title
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
from .values import AccountId

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
            user_id=UserId(command.user_id),
            name=Title(command.name),
            balance=Money(command.balance),
            account_type=command.account_type,
            currency=command.currency,
        )
        acc_id = await self._repository.save(new_account)

        await self._publish(account=new_account)

        logger.info("Новый счёт #%s создан", AccountId(acc_id).short)
        return new_account

    async def find_account_by_id(self, command: GetAccountCommand) -> Account:
        """
        Поиск счёта по уникальному id
        Если счёта нет - ошибка
        """

        if not (
            account := await self._repository.get_by_id(
                account_id=command.account_id,
                user_id=command.user_id,
            )
        ):
            logger.warning("Счёт #%s не найден", AccountId(command.account_id).short)
            raise AccountNotFoundException

        logger.info(f"Счёт #{AccountId(command.account_id).short} получен")
        return account

    async def find_accounts_by_user_id(self, user_id: str) -> list[Account]:
        """Поиск всех счетов пользователя по его уникальному id"""

        accounts = await self._repository.get_by_user_id(user_id)
        logger.info(f"Счёта пользователя #{UserId(user_id).short} получены")
        return accounts

    async def delete_account(self, command: GetAccountCommand) -> None:
        """Удаление счёта по id"""

        account = await self.find_account_by_id(command=command)
        await self._repository.delete(
            account_id=account.id.as_generic_type(),
            user_id=account.user_id.as_generic_type(),
        )
        logger.info("Счёт #%s был удален", account.id.short)
        return

    async def _publish(self, account: Account):
        """Публикует события"""

        published = []
        for event in account.events:
            try:
                await self._publisher.publish(event)
                published.append(event)
            except Exception as e:
                logger.error(str(e))
                raise

        for event in published:
            account.events.remove(event)


class AccountService(AccountCRUDService):
    """Сервис управления счетами пользователей"""

    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        account_publisher: AccountEventPublisherProtocol,
    ):
        super().__init__(account_repo, account_publisher)

    async def update_balance(self, command: UpdateAccountBalanceCommand) -> None:
        """Обновление баланса счета"""

        account = await self.find_account_by_id(
            command=GetAccountCommand(
                account_id=command.account_id, user_id=command.user_id
            )
        )

        is_updated = account.update_balance(
            new_balance=Money(command.new_balance),
            is_monthly_closing=command.is_monthly_closing,
        )
        if not is_updated:
            logger.info("Баланс счёта #%s не изменен", account.id.short)
            return

        await self._repository.update(
            account_id=command.account_id,
            user_id=command.user_id,
            upd_data=AccountDTO.from_entity_to_dict(
                account, excludes=["id", "user_id"]
            ),
        )
        logger.info("Баланс счета #%s обновлен", account.id.short)
        await self._publish(account=account)


def get_account_service(
    acc_repo: AccountRepositoryDep, acc_publisher: AccountEventPublisherDep
) -> AccountService:
    return AccountService(account_repo=acc_repo, account_publisher=acc_publisher)
