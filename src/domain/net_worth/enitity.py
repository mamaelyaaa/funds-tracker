from dataclasses import dataclass

from domain.accounts.entity import Account
from domain.users.values import UserId
from pydantic.types import Decimal


@dataclass(frozen=True, kw_only=True)
class NetWorth:
    """Доменная модель чистого капитала"""

    user_id: UserId
    accounts: list[Account]

    @property
    def total_balance(self) -> Decimal:
        return Decimal(sum(account.balance for account in self.accounts))

    # @property
    # def month_profit(self) -> float:
    #     return ...
    #
    @property
    def total_profit(self) -> float:
        return ...
