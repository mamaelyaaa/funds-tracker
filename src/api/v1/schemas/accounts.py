from pydantic import BaseModel, Field

from accounts.domain import AccountType


class CreateAccountSchema(BaseModel):
    name: str
    initial_balance: float = Field(alias="initialBalance")
    account_type: AccountType = Field(alias="accountType")


class AccountCreatedResponse(BaseModel):
    account_id: str = Field(alias="accountId")
