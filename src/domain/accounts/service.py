import asyncio
import logging

from api.schemas import PaginationMetaSchema
from domain.users.entity import User
from domain.users.values import UserId
from domain.values import Money, Title
from infra.database.specification import PaginationSpecification
from .commands import (
    CreateAccountCommand,
    GetAccountCommand,
    UpdateAccountBalanceCommand,
    GetAccountsCommand,
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

logger = logging.getLogger("account.service")


class AccountCRUDService:

    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        account_publisher: AccountEventPublisherProtocol,
    ):
        self.repository = account_repo
        self.publisher = account_publisher

    async def create_account(self, command: CreateAccountCommand) -> Account:
        """
        Создаем новый счет

        - Если счёт для текущего пользователя уже существует - ошибка
        - Если превышен лимит активных счётов пользователя - ошибка
        """

        # Проверка на существование счёта с таким названием
        check = await self.repository.is_name_taken(
            user_id=command.user_id, name=command.name
        )
        if check:
            logger.warning(
                "Попытка создания дубликата счета: имя '%s' уже занято",
                command.name,
                extra={
                    "user_id": UserId(command.user_id).short,
                },
            )
            raise AccountAlreadyCreatedException

        # Проверка на лимит активных счетов пользователя
        count = await self.repository.count_by_user_id(command.user_id)
        if count >= User.MAX_ACCOUNTS:
            logger.warning(
                f"Превышен лимит активных счётов: %d из %d",
                count,
                User.MAX_ACCOUNTS,
                extra={"user_id": UserId(command.user_id).short},
            )
            raise TooManyAccountsForUserException

        new_account = Account(
            user_id=UserId(command.user_id),
            name=Title(command.name),
            balance=Money(command.balance),
            type=command.account_type,
            currency=command.currency,
        )
        acc_id = await self.repository.save(new_account)
        await self._publish(account=new_account)

        logger.info(
            "Новый счёт #%s создан",
            AccountId(acc_id).short,
            extra={"user_id": UserId(command.user_id).short},
        )
        return new_account

    async def find_account_by_id(self, command: GetAccountCommand) -> Account:
        """
        Поиск счёта по уникальному id
        Если счёта нет - ошибка
        """

        if not (
            account := await self.repository.find_one(
                id=command.account_id, user_id=command.user_id
            )
        ):
            logger.warning("Счёт #%s не найден", AccountId(command.account_id).short)
            raise AccountNotFoundException

        logger.info(f"Счёт #{AccountId(command.account_id).short} получен")
        return account

    async def find_accounts_by_user_id(
        self,
        command: GetAccountsCommand,
    ) -> tuple[list[Account], PaginationMetaSchema]:
        """
        Поиск всех счетов пользователя по его уникальному id с пагинацией
        """

        accounts, account_count = await asyncio.gather(
            self.repository.find_all(
                PaginationSpecification.from_pagination_command(command.pagination),
                user_id=command.user_id,
            ),
            self.repository.count_by_user_id(user_id=command.user_id),
        )

        logger.info("Счёта пользователя #%s получены", UserId(command.user_id).short)

        return accounts, PaginationMetaSchema(
            page=command.pagination.page,
            limit=command.pagination.limit,
            total_found=account_count,
        )

    async def delete_account(self, command: GetAccountCommand) -> None:
        """Удаление счёта по id"""

        account = await self.find_account_by_id(command=command)
        await self.repository.delete_one(
            id=account.id.as_generic_type(),
            user_id=account.user_id.as_generic_type(),
        )
        logger.info("Счёт #%s был удален", account.id.short)
        return

    async def _publish(self, account: Account):
        """Публикует события"""

        published = []
        for event in account.events:
            try:
                await self.publisher.publish(event)
                published.append(event)
            except Exception as e:
                logger.exception(
                    "Не удалось опубликовать событие типа %s для счета %s",
                    type(event).__name__,
                    account.id.short,
                    extra={"account_id": account.id.short},
                )
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

        if account.balance == Money(command.new_balance):
            logger.info("Баланс счёта #%s не изменен", account.id.short)
            return

        account.update_balance(
            new_balance=Money(command.new_balance),
            is_monthly_closing=command.is_monthly_closing,
        )

        await self.repository.update(
            id=command.account_id,
            user_id=command.user_id,
            upd_data=AccountDTO.from_entity_to_dict(
                account, excludes=["id", "user_id"]
            ),
        )
        await self._publish(account=account)
        logger.info("Баланс счета #%s обновлен", account.id.short)
