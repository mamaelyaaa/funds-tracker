from typing import Annotated

from fastapi import APIRouter, Depends, status, Body

from api.schemas import (
    BaseResponseSchema,
    BaseResponseDetailSchema,
    BaseExceptionSchema,
)
from api.v1.schemas.accounts import (
    CreateAccountSchema,
    AccountDetailSchema,
)
from domain.accounts.commands import (
    CreateAccountCommand,
    GetAccountCommand,
    UpdateAccountBalanceCommand,
)
from domain.accounts.dto import AccountDTO
from domain.accounts.entity import Account
from domain.accounts.service import AccountServiceDep
from domain.users.dependencies import get_user

router = APIRouter(
    prefix="/users/{user_id}/accounts",
    tags=["Счета🏦"],
    dependencies=[Depends(get_user)],
)


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
            "description": "Невалидный баланс или название счёта",
        },
    },
)
async def create_account(
    account_service: AccountServiceDep,
    schema: CreateAccountSchema,
    user_id: str,
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
        detail=AccountDTO.from_entity_to_dict(account),
        metadata={},
    )


@router.get(
    "",
    response_model=BaseResponseDetailSchema[list[AccountDetailSchema], dict],
)
async def get_accounts(
    account_service: AccountServiceDep,
    user_id: str,
):
    """Получение счетов пользователя"""

    accounts = await account_service.find_accounts_by_user_id(user_id=user_id)

    return BaseResponseDetailSchema(
        message=f"Получение счётов пользователя",
        detail=[AccountDTO.from_entity_to_dict(account) for account in accounts],
        metadata={},
    )


@router.get(
    "/{account_id}",
    response_model=BaseResponseDetailSchema[AccountDetailSchema, dict],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": BaseExceptionSchema,
            "description": "Счёт не найден",
        }
    },
)
async def get_account_by_id(
    account_service: AccountServiceDep,
    account_id: str,
    user_id: str,
):
    """Получение счета пользователя по уникальному id"""

    account = await account_service.find_account_by_id(
        command=GetAccountCommand(account_id=account_id, user_id=user_id)
    )

    return BaseResponseDetailSchema(
        message=f"Получение счёта пользователя",
        detail=AccountDTO.from_entity_to_dict(account),
        metadata={},
    )


@router.put(
    "/{account_id}/balance",
    response_model=BaseResponseSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": BaseExceptionSchema,
            "description": "Счёт не найден",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BaseExceptionSchema,
            "description": "Невалидный счёт",
        },
    },
)
async def update_account_balance(
    account_service: AccountServiceDep,
    account_id: str,
    user_id: str,
    actual_balance: float = Body(default=0, embed=True),
):
    """
    Обновление баланса счёта и фоновое обновление полного капитала пользователя

    Возвращает 200 статус даже если баланс не изменился
    """

    await account_service.update_balance(
        command=UpdateAccountBalanceCommand(
            account_id=account_id,
            user_id=user_id,
            new_balance=actual_balance,
        )
    )

    return BaseResponseSchema(message="Баланс счёта обновлен")


@router.delete(
    "/{account_id}",
    response_model=BaseResponseSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": BaseExceptionSchema,
            "description": "Счёт не найден",
        }
    },
)
async def delete_balance(
    account_service: AccountServiceDep,
    account_id: str,
    user_id: str,
):
    """Удаляет счёт"""

    await account_service.delete_account(
        command=GetAccountCommand(account_id=account_id, user_id=user_id)
    )
    return BaseResponseSchema(message="Счёт удален")


async def get_account(
    account_service: AccountServiceDep,
    account_id: str,
    user_id: str,
) -> Account:
    account = await account_service.find_account_by_id(
        command=GetAccountCommand(
            account_id=account_id,
            user_id=user_id,
        )
    )
    return account


AccountDep = Annotated[Account, Depends(get_account)]
