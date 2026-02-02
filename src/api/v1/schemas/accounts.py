from datetime import datetime
from typing import Any

from pydantic import BaseModel

from domain.accounts.entity import AccountType, AccountCurrency, Account


class CreateAccountSchema(BaseModel):
    name: str
    initial_balance: float
    account_type: AccountType
    currency: AccountCurrency


class AccountDetailSchema(BaseModel):
    id: str
    name: str
    type: AccountType
    balance: float
    currency: AccountCurrency
    created_at: datetime

    @classmethod
    def from_domain(cls, account: Account) -> "AccountDetailSchema":
        return AccountDetailSchema(
            id=account.id.value,
            name=account.name.value,
            balance=account.balance,
            currency=account.currency,
            type=account.type,
            created_at=account.created_at,
        )

    @staticmethod
    def to_domain(data: dict[str, Any]) -> Account:
        return Account(**data)
