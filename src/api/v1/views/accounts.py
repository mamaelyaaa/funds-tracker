from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi import Body

from api.schemas import (
    BaseResponseSchema,
    BaseResponseDetailSchema,
    BaseExceptionSchema,
)
from api.v1.schemas.accounts import (
    CreateAccountSchema,
    AccountDetailSchema,
)
from domain.accounts.comands import CreateAccountCommand, UpdateAccountBalanceCommand
from domain.accounts.service import AccountService, get_account_service
from domain.users.dependencies import UserDep

router = APIRouter(
    prefix="/users/{user_id}/accounts",
    tags=["Счета🏦"],
)

AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]


@router.post(
    "",
    response_model=BaseResponseDetailSchema[AccountDetailSchema, dict],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "model": BaseResponseDetailSchema[AccountDetailSchema, dict],
            "description": "Счёт создан",
        },
        409: {
            "model": BaseExceptionSchema,
            "description": "Превышен лимит активных счётов ИЛИ Счёт с таким названием уже существует",
        },
        400: {
            "model": BaseExceptionSchema,
            "description": "Невалидные символы для названия счёта (пустые строки не попадают под эту ошибку)",
        },
    },
)
async def create_account(
    account_service: AccountServiceDep,
    schema: CreateAccountSchema,
    user_id: str,
    user: UserDep,
):
    """Создание нового счёта"""

    account = await account_service.create_account(
        command=CreateAccountCommand(
            account_type=schema.account_type,
            name=schema.name,
            balance=schema.initial_balance,
            currency=schema.currency,
            user_id=user_id,
        )
    )

    return BaseResponseDetailSchema(
        message=f"Счет '{schema.name}' успешно создан",
        detail=AccountDetailSchema.from_domain(account),
        metadata={},
    )


@router.get(
    "",
    response_model=BaseResponseDetailSchema[list[AccountDetailSchema], dict],
)
async def get_accounts(
    account_service: AccountServiceDep,
    user_id: str,
    user: UserDep,
):
    """Получение счетов пользователя"""

    accounts = await account_service.find_accounts_by_user_id(user_id=user_id)

    return BaseResponseDetailSchema(
        message=f"Получение счётов пользователя",
        detail=[AccountDetailSchema.from_domain(account) for account in accounts],
        metadata={},
    )


@router.get(
    "/{account_id}",
    response_model=BaseResponseDetailSchema[AccountDetailSchema, dict],
)
async def get_account(
    account_service: AccountServiceDep,
    account_id: str,
    user_id: str,
    user: UserDep,
):
    """Получение счета пользователя по уникальному id"""

    account = await account_service.find_account_by_id(account_id=account_id)

    return BaseResponseDetailSchema(
        message=f"Получение счёта пользователя",
        detail=AccountDetailSchema.from_domain(account),
        metadata={},
    )


@router.put(
    "/{account_id}/balance",
    response_model=BaseResponseSchema,
)
async def update_account_balance(
    account_service: AccountServiceDep,
    account_id: str,
    user_id: str,
    user: UserDep,
    actual_balance: float = Body(embed=True),
):
    """
    Обновление баланса счёта и фоновое обновление полного капитала пользователя

    Возвращает 200 статус даже если баланс не изменился
    """

    await account_service.update_balance(
        command=UpdateAccountBalanceCommand(
            account_id=account_id,
            new_balance=actual_balance,
        )
    )

    return BaseResponseSchema(message="Баланс счёта обновлен")


@router.delete("/{account_id}", response_model=BaseResponseSchema)
async def delete_balance(
    account_service: AccountServiceDep,
    account_id: str,
    user_id: str,
    user: UserDep,
):
    """Удаляет счёт"""

    await account_service.delete_account(account_id=account_id)
    return BaseResponseSchema(message="Счёт удален")
