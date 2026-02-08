from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.schemas import BaseResponseDetailSchema, BaseApiModel, BaseExceptionSchema
from api.v1.schemas.histories import (
    HistoryDetailSchema,
    GetHistorySchema,
    HistoryPercentChangeSchema,
)
from api.v1.views.accounts import get_account, AccountDep
from domain.histories.commands import GetAccountHistoryCommand
from domain.histories.service import HistoryServiceDep
from domain.users.dependencies import get_user

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


class HistoryMetadata(BaseApiModel):
    start_date: datetime
    period: str


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
        detail=[HistoryDetailSchema.from_model(row) for row in history],
        message="История счёта успешно получена",
        metadata=HistoryMetadata(**history_service.metadata),
    )


@router.get(
    "/percent-change",
    response_model=BaseResponseDetailSchema[
        HistoryPercentChangeSchema, HistoryMetadata
    ],
)
async def get_percent_change_by_time_interval(
    history_service: HistoryServiceDep,
    schema: Annotated[GetHistorySchema, Depends()],
    account_id: str,
    user_id: str,
):
    """Считает процентный доход счёта за определенный интервал времени"""

    percent_change = await history_service.get_history_percent_change(
        command=GetAccountHistoryCommand(
            interval=schema.interval,
            account_id=account_id,
            user_id=user_id,
        )
    )
    return BaseResponseDetailSchema(
        message="Получен доход счёта",
        detail=HistoryPercentChangeSchema(
            percent_profit=float(f"{percent_change:.4f}")
        ),
        metadata=HistoryMetadata(**history_service.metadata),
    )
