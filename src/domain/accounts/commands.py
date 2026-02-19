from dataclasses import dataclass

from .values import AccountType, AccountCurrency


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
class UpdateAccountBalanceCommand:
    """Команда для обновления баланса счёта"""

    user_id: str
    account_id: str
    new_balance: float


@dataclass(frozen=True)
class UpdateAccountNameCommand:
    """Команда для обновления названия счёта"""

    user_id: str
    account_id: str
    new_name: str
