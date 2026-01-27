from pydantic import BaseModel, Field

from accounts.domain import AccountType, AccountCurrency


class CreateAccountSchema(BaseModel):
    name: str
    initial_balance: float = Field(alias="initialBalance")
    account_type: AccountType = Field(alias="accountType")
    currency: AccountCurrency


class AccountIdResponse(BaseModel):
    account_id: str = Field(alias="accountId")
