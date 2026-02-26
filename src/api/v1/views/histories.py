from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.schemas import BaseResponseDetailSchema, BaseExceptionSchema
from api.v1.schemas.histories import (
    HistoryDetailSchema,
    GetHistorySchema,
    HistoryMetadata,
    HistoryProfitSchema,
)
from domain.histories.commands import GetAccountHistoryCommand
from domain.histories.dto import HistoryDTO
from domain.histories.service import HistoryServiceDep
from domain.users.dependencies import get_user
from .accounts import get_account

router = APIRouter(
    prefix="/users/{user_id}/accounts/{account_id}/history",
    tags=["История счетов⌚"],
    dependencies=[Depends(get_user), Depends(get_account)],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": BaseExceptionSchema,
            "description": "Не найден пользователь ИЛИ не найден счёт пользователя",
        }
    },
)


@router.get(
    "",
    response_model=BaseResponseDetailSchema[list[HistoryDetailSchema], HistoryMetadata],
)
async def get_account_history(
    history_service: HistoryServiceDep,
    schema: Annotated[GetHistorySchema, Depends()],
    account_id: str,
    user_id: str,
):
    """
    Получение истории счёта

    Система группирует записи по периодам, для удобного отображения и экономии ресурсов.

    В метаданных содержится информация:

    - start_date: Дата начала интервала для отображения (может не совпадать с первой записью)
    - period: Период для группировки записей

    `Пример`: Интервал: `1 месяц` тогда период: `days`. Система группирует записи по дням и если за день было
    несколько записей - выведет *крайнюю* по времени

    `Разбиение интервалов`:
    - **1Day**: период "minutes"
    - **1Week**: период "hours"
    - **1Month**: период "days"
    - **6Month**: период "weeks"
    - **1Year**: период "months"
    - **All**: период "years"
    """

    history = await history_service.get_account_history(
        command=GetAccountHistoryCommand(
            account_id=account_id,
            user_id=user_id,
            interval=schema.interval,
        )
    )

    return BaseResponseDetailSchema(
        detail=[HistoryDTO.from_entity_to_dict(row) for row in history],
        message="История счёта успешно получена",
        metadata=HistoryMetadata(**history_service.metadata),
    )


@router.get(
    "/profit",
    response_model=BaseResponseDetailSchema[HistoryProfitSchema, HistoryMetadata],
)
async def get_profit_by_time_interval(
    history_service: HistoryServiceDep,
    schema: Annotated[GetHistorySchema, Depends()],
    account_id: str,
    user_id: str,
):
    """Считает процентный доход счёта за определенный интервал времени"""

    profit = await history_service.get_history_profit(
        command=GetAccountHistoryCommand(
            interval=schema.interval,
            account_id=account_id,
            user_id=user_id,
        )
    )
    return BaseResponseDetailSchema(
        message="Получен доход счёта",
        detail=HistoryProfitSchema(**profit),
        metadata=HistoryMetadata(**history_service.metadata),
    )
