from typing import Protocol

from domain.users.values import UserId


class NetWorthRepositoryProtocol(Protocol):

    async def get_user_total_balance(self, user_id: UserId) -> float:
        pass
