from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, Field

from accounts.domain import AccountType, AccountCurrency, Account


class CreateAccountSchema(BaseModel):
    name: str
    initial_balance: float = Field(alias="initialBalance")
    account_type: AccountType = Field(alias="accountType")
    currency: AccountCurrency


class AccountIdResponse(BaseModel):
    account_id: str = Field(alias="accountId")


class AccountDetailSchema(BaseModel):
    id: str
    user_id: str
    name: str
    type: AccountType
    balance: float
    currency: AccountCurrency
    created_at: datetime

    @classmethod
    def from_orm(cls, account: Account) -> "AccountDetailSchema":
        return AccountDetailSchema(
            id=account.id.value,
            user_id=account.user_id.value,
            name=account.name.value,
            balance=account.balance,
            currency=account.currency,
            type=account.type,
            created_at=account.created_at,
        )
