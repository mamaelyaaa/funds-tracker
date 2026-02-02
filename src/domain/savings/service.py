import logging

from domain.accounts.values import AccountId
from domain.savings.domain import SavingsHistory
from domain.savings.repository import SavingsHistoryRepositoryProtocol
from infra.repositories.savings import SavingsRepositoryDep

logger = logging.getLogger(__name__)


class SavingsHistoryService:

    def __init__(self, savings_repo: SavingsHistoryRepositoryProtocol):
        self._repository = savings_repo

    async def make_account_screenshot(self, account_id: str, balance: float) -> str:
        logger.debug(account_id)
        savings = SavingsHistory(account_id=AccountId(account_id), balance=balance)
        await self._repository.save(savings)
        return savings.id.value


def get_savings_service(savings_repo: SavingsRepositoryDep) -> SavingsHistoryService:
    return SavingsHistoryService(savings_repo)
