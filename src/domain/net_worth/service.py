from domain.users.values import UserId
from infra.repositories.net_worth import NetWorthRepositoryDep
from .repository import NetWorthRepositoryProtocol


class NetWorthService:

    def __init__(self, nw_repo: NetWorthRepositoryProtocol):
        self._nw_repo = nw_repo

    async def calculate_total_balance(self, user_id: str) -> float:
        total_balance = await self._nw_repo.get_user_total_balance(UserId(user_id))
        return total_balance

    async def calculate_monthly_profit(self):
        pass


def get_net_worth_service(nw_repo: NetWorthRepositoryDep) -> NetWorthService:
    return NetWorthService(nw_repo)
