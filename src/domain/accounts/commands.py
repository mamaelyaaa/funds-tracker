from dataclasses import dataclass

from domain.commands import PaginationCommand
from .entities import AccountType, AccountCurrency


@dataclass(frozen=True)
class CreateAccountCommand:
    """Команда для создания счёта"""

    user_id: str
    name: str
    balance: float
    account_type: AccountType
    currency: AccountCurrency


@dataclass(frozen=True)
class GetAccountCommand:
    """Команда для получения баланса счёта"""

    user_id: str
    account_id: str


@dataclass(frozen=True)
class GetAccountsCommand:
    """Команда для получения баланса счёта"""

    user_id: str
    pagination: PaginationCommand


@dataclass(frozen=True, kw_only=True)
class UpdateAccountBalanceCommand:
    """Команда для обновления баланса счёта"""

    user_id: str
    account_id: str
    new_balance: float
    is_monthly_closing: bool = False
