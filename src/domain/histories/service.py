import logging

from domain.accounts.values import AccountId
from domain.histories.commands import SaveHistoryCommand, GetAccountHistoryCommand
from domain.histories.domain import AccountHistory
from domain.histories.repository import HistoryRepositoryProtocol
from infra.repositories.histories import HistoryRepositoryDep

logger = logging.getLogger(__name__)


class HistoryService:

    def __init__(self, savings_repo: HistoryRepositoryProtocol):
        self._repository = savings_repo

    async def save_account_history(self, command: SaveHistoryCommand) -> str:
        savings = AccountHistory(
            account_id=AccountId(command.account_id),
            balance=command.balance,
        )
        await self._repository.save(savings)
        return savings.id.value

    async def get_account_history(
        self, command: GetAccountHistoryCommand
    ) -> list[AccountHistory]:
        history = await self._repository.get_by_acc_id(
            account_id=AccountId(command.account_id),
            order_by="created_at",
            asc=False,
            limit=command.pagination.limit,
            offset=command.pagination.page_offset,
        )
        return history


def get_history_service(histories_repo: HistoryRepositoryDep) -> HistoryService:
    return HistoryService(histories_repo)
