from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import Body

from accounts.service import AccountService, get_account_service
from api.schemas import BaseResponseSchema, BaseResponseDetailSchema
from api.v1.schemas.accounts import (
    CreateAccountSchema,
    AccountIdResponse,
    AccountDetailSchema,
)
from users.dependencies import get_user
from users.domain import User

router = APIRouter(
    prefix="/users/{user_id}/accounts",
    tags=["Счета🏦"],
)

AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]


@router.post(
    "",
    response_model=BaseResponseDetailSchema[AccountIdResponse, dict],
)
async def create_account(
    account_service: AccountServiceDep,
    schema: CreateAccountSchema,
    user_id: str,
    user: Annotated[User, Depends(get_user)],
):
    """Создание нового счёта"""

    account_id = await account_service.create_account(
        account_type=schema.account_type,
        name=schema.name,
        initial_balance=schema.initial_balance,
        currency=schema.currency,
        user_id=user_id,
    )

    return BaseResponseDetailSchema(
        message=f"Счет '{schema.name}' успешно создан",
        detail=AccountIdResponse(accountId=account_id.value),
    )


@router.get(
    "",
    response_model=BaseResponseDetailSchema[list[AccountDetailSchema], dict],
)
async def get_accounts(
    account_service: AccountServiceDep,
    user_id: str,
    user: Annotated[User, Depends(get_user)],
):
    """Получение счетов пользователя"""

    accounts = await account_service.find_accounts_by_user_id(user_id=user_id)

    return BaseResponseDetailSchema(
        message=f"Получение счётов пользователя",
        detail=[AccountDetailSchema.from_orm(account) for account in accounts],
    )


@router.get(
    "/{account_id}",
    response_model=BaseResponseDetailSchema[AccountDetailSchema, dict],
)
async def get_account(
    account_service: AccountServiceDep,
    account_id: str,
    user: Annotated[User, Depends(get_user)],
    user_id: str,
):
    """Получение счета пользователя по уникальному id"""

    account = await account_service.find_account_by_id(account_id=account_id)

    return BaseResponseDetailSchema(
        message=f"Получение счёта пользователя",
        detail=AccountDetailSchema.from_orm(account),
    )


@router.put(
    "/{account_id}/balance",
    response_model=BaseResponseSchema,
)
async def update_account_balance(
    account_service: AccountServiceDep,
    account_id: str,
    user_id: str,
    user: Annotated[User, Depends(get_user)],
    actual_balance: float = Body(embed=True),
):
    """
    Обновление баланса счёта и фоновое обновление полного капитала пользователя

    Возвращает 200 статус даже если баланс не изменился
    """

    await account_service.set_new_balance(
        account_id=account_id,
        actual_balance=actual_balance,
    )

    return BaseResponseSchema(message="Баланс счёта обновлен")


@router.delete("/{account_id}", response_model=BaseResponseSchema)
async def delete_balance(
    account_service: AccountServiceDep,
    account_id: str,
    user_id: str,
    user: Annotated[User, Depends(get_user)],
):
    """Удаляет счёт"""

    await account_service.delete_account(account_id=account_id)
    return BaseResponseSchema(message="Счёт удален")
