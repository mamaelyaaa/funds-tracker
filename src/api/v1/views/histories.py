from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.schemas import BaseResponseDetailSchema, BaseExceptionSchema
from api.v1.dependencies.accounts import get_account
from api.v1.dependencies.histories import HistoryServiceDep
from api.v1.dependencies.users import get_user
from api.v1.schemas.histories import (
    HistoryDetailSchema,
    GetHistorySchema,
    HistoryMetadataSchema,
    HistoryProfitSchema,
    HistoryFullSchema,
)
from domain.histories.commands import GetAccountHistoryCommand
from domain.histories.dto import HistoryDTO

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
    response_model=BaseResponseDetailSchema[HistoryFullSchema, HistoryMetadataSchema],
)
async def get_account_history(
    history_service: HistoryServiceDep,
    schema: Annotated[GetHistorySchema, Depends()],
    account_id: str,
    user_id: str,
):
    """
    Получение истории и профита счёта

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

    history, profit, metadata = await history_service.get_account_history(
        command=GetAccountHistoryCommand(
            account_id=account_id,
            user_id=user_id,
            interval=schema.interval,
        )
    )

    return BaseResponseDetailSchema(
        detail=HistoryFullSchema(
            profit=HistoryProfitSchema(**asdict(profit)),
            history=[
                HistoryDetailSchema.model_validate(HistoryDTO.from_entity_to_dict(row))
                for row in history
            ],
        ),
        message="История счёта успешно получена",
        metadata=HistoryMetadataSchema(**asdict(metadata)),
    )
