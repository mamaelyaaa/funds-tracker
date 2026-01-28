import logging

from infra.publishers.accounts import AccountEventPublisherDep
from infra.repositories.accounts import AccountRepositoryDep
from .domain import (
    Account,
    AccountType,
    AccountId,
    BalanceUpdatedEvent,
    AccountCurrency,
)
from .exceptions import AccountNotFoundException
from .publisher import AccountEventPublisherProtocol
from .repository import AccountRepositoryProtocol

logger = logging.getLogger(__name__)


class AccountService:
    """Сервис управления счетами пользователей"""

    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        account_publisher: AccountEventPublisherProtocol,
    ):
        self._repository = account_repo
        self._publisher = account_publisher

    async def create_account(
        self,
        name: str,
        initial_balance: float,
        account_type: AccountType,
        currency: AccountCurrency,
    ) -> AccountId:
        """Создаем новый счет"""

        new_account = Account.create(
            name=name,
            balance=initial_balance,
            account_type=account_type,
            currency=currency,
        )
        acc_id = await self._repository.save(new_account)
        logger.info("Новый счёт #%s создан", acc_id.short)
        return acc_id

    async def set_new_balance(
        self, account_id: AccountId, actual_balance: float
    ) -> None:
        """Обновляем баланс счета"""

        account = await self._find_account_by_id(account_id)
        account.update_balance(actual_balance)

        await self._repository.save(account)
        logger.info("Баланс счета #%s обновлен", account.id.short)

        for event in account.events:
            if isinstance(event, BalanceUpdatedEvent):
                await self._publisher.publish_balance_changed(event)

        account.events.clear()
        return

    async def rename_account(self, account_id: AccountId, new_name: str) -> None:
        account = await self._find_account_by_id(account_id)
        account.rename_account(new_name)

        await self._repository.save(account)
        logger.info("Название счета #%s обновлено", account.id.short)
        return

    async def delete_account(self, account_id: AccountId) -> None:
        account = await self._find_account_by_id(account_id)

        await self._repository.delete(account.id)
        logger.info("Счёт #%s был удален", account.id.short)
        return

    async def _find_account_by_id(self, account_id: AccountId) -> Account:
        if not (account := await self._repository.get_by_id(account_id)):
            logger.warning("Счёт #%s не найден", account_id.short)
            raise AccountNotFoundException
        return account


def get_account_service(
    acc_repo: AccountRepositoryDep,
    acc_publisher: AccountEventPublisherDep,
) -> AccountService:
    return AccountService(
        account_repo=acc_repo,
        account_publisher=acc_publisher,
    )
