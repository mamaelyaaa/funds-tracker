from accounts.values import AccountId
from infra.repositories.savings import SavingsRepositoryDep
from savings.domain import SavingsHistory
from savings.repository import SavingsHistoryRepositoryProtocol


class SavingsHistoryService:

    def __init__(self, savings_repo: SavingsHistoryRepositoryProtocol):
        self._repository = savings_repo

    async def make_account_screenshot(self, account_id: str, balance: float) -> str:
        savings = SavingsHistory(account_id=AccountId(account_id), balance=balance)
        await self._repository.save(savings)
        return savings.id.value


def get_savings_service(savings_repo: SavingsRepositoryDep) -> SavingsHistoryService:
    return SavingsHistoryService(savings_repo)
