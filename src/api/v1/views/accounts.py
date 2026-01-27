from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import Body

from accounts.domain import AccountId
from accounts.service import AccountService, get_account_service
from api.schemas import BaseResponseSchema, BaseResponseDetailSchema
from api.v1.schemas.accounts import CreateAccountSchema, AccountIdResponse

router = APIRouter(prefix="/accounts", tags=["Счета🏦"])

AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]


@router.post("", response_model=AccountIdResponse)
async def create_account(
    account_service: AccountServiceDep, schema: CreateAccountSchema
):
    """Создание нового счёта"""

    account_id = await account_service.create_account(
        account_type=schema.account_type,
        name=schema.name,
        initial_balance=schema.initial_balance,
        currency=schema.currency,
    )
    return AccountIdResponse(accountId=account_id.value)


@router.put(
    "/{account_id}/balance", response_model=BaseResponseDetailSchema[AccountIdResponse]
)
async def update_account_balance(
    account_service: AccountServiceDep,
    account_id: str,
    actual_balance: float = Body(embed=True),
):
    """Обновляет баланс счёта"""

    await account_service.set_new_balance(
        account_id=AccountId(account_id), actual_balance=actual_balance
    )

    return BaseResponseDetailSchema(
        message="Баланс счёта обновлен",
        detail=AccountIdResponse(accountId=account_id),
    )


@router.delete("/{account_id}", response_model=BaseResponseSchema)
async def delete_balance(
    account_service: AccountServiceDep,
    account_id: str,
):
    """Удаляет счёт"""

    await account_service.delete_account(account_id=AccountId(account_id))
    return BaseResponseSchema(message="Счёт удален")
