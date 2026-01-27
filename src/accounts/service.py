import logging

from infra.publishers.accounts import AccountEventPublisherDep
from infra.repositories.accounts import AccountRepositoryDep
from .domain import Account, AccountType, AccountId, BalanceUpdatedEvent
from .exceptions import AccountNotFoundException
from .publisher import AccountEventPublisherProtocol
from .repository import AccountRepositoryProtocol

logger = logging.getLogger(__name__)


class AccountService:

    def __init__(
        self,
        account_repo: AccountRepositoryProtocol,
        account_publisher: AccountEventPublisherProtocol,
    ):
        self._repository = account_repo
        self._publisher = account_publisher

    async def create_account(
        self, name: str, initial_balance: float, account_type: AccountType
    ) -> AccountId:
        """Создаем новый счет"""

        new_account = Account.create(
            name=name,
            balance=initial_balance,
            account_type=account_type,
        )
        acc_id = await self._repository.save(new_account)
        logger.info("Новый счёт #%s создан", acc_id.short)
        return acc_id

    async def set_new_balance(
        self, account_id: AccountId, actual_balance: float
    ) -> None:
        """Обновляем баланс счета"""

        account = await self._repository.get_by_id(account_id)
        if not account:
            logger.warning("Счёт #%s не найден", account_id.short)
            raise AccountNotFoundException

        account.update_balance(actual_balance)
        await self._repository.save(account)
        logger.info("Баланс счета #%s обновлен", account.id.short)

        for event in account.events:
            if isinstance(event, BalanceUpdatedEvent):
                await self._publisher.publish_balance_changed(event)

        account.events.clear()
        return


def get_account_service(
    acc_repo: AccountRepositoryDep,
    acc_publisher: AccountEventPublisherDep,
) -> AccountService:
    return AccountService(
        account_repo=acc_repo,
        account_publisher=acc_publisher,
    )
