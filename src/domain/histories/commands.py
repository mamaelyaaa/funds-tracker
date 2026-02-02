from dataclasses import dataclass

from domain.commands import PaginationCommand


@dataclass(frozen=True)
class SaveHistoryCommand:
    account_id: str
    balance: float


@dataclass(frozen=True)
class GetAccountHistoryCommand:
    account_id: str
    pagination: PaginationCommand
