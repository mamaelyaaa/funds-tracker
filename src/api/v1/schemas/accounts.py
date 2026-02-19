from datetime import datetime

from api.schemas import BaseApiModel
from domain.accounts.entity import AccountType, AccountCurrency


class CreateAccountSchema(BaseApiModel):
    name: str
    initial_balance: float
    account_type: AccountType
    currency: AccountCurrency


class AccountDetailSchema(BaseApiModel):
    id: str
    name: str
    type: AccountType
    balance: float
    currency: AccountCurrency
    created_at: datetime
