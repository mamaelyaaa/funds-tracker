from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import Body, Query

from accounts.domain import AccountId
from accounts.service import AccountService, get_account_service
from api.v1.schemas.accounts import CreateAccountSchema, AccountCreatedResponse

router = APIRouter(prefix="/accounts", tags=["Счета🏦"])

AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]


@router.post("", response_model=AccountCreatedResponse)
async def create_account(
    account_service: AccountServiceDep, schema: CreateAccountSchema
):
    """Создание нового счета"""

    account_id = await account_service.create_account(
        account_type=schema.account_type,
        name=schema.name,
        initial_balance=schema.initial_balance,
    )
    return AccountCreatedResponse(accountId=account_id.value)


@router.put("/{account_id}/balance")
async def update_account_balance(
    account_service: AccountServiceDep,
    account_id: str,
    actual_balance: float = Body(embed=True),
):
    await account_service.set_new_balance(
        account_id=AccountId(account_id), actual_balance=actual_balance
    )
    return {"ok": True}
