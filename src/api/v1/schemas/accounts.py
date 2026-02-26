from datetime import datetime

from pydantic import Field

from api.schemas import BaseApiModel
from domain.accounts.entity import AccountType, AccountCurrency


class CreateAccountSchema(BaseApiModel):
    name: str
    initial_balance: float = Field(default=0, ge=0)
    account_type: AccountType
    currency: AccountCurrency


class UpdateAccountSchema(BaseApiModel):
    actual_balance: float
    is_monthly_closing: bool = False
    occurred_at: datetime


class AccountDetailSchema(BaseApiModel):
    id: str
    name: str
    type: AccountType
    balance: float
    currency: AccountCurrency
    created_at: datetime
