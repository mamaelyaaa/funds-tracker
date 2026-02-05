from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.schemas import BaseResponseDetailSchema
from api.v1.schemas.histories import HistoryDetailSchema, GetHistorySchema
from domain.histories.commands import GetAccountHistoryCommand
from domain.histories.service import HistoryServiceDep
from domain.users.dependencies import UserDep

router = APIRouter(
    prefix="/users/{user_id}/accounts/{account_id}",
    tags=["История счетов⌚"],
)


class HistoryMetadata(BaseModel):
    start_date: datetime
    period: str


@router.get(
    "/history",
    response_model=BaseResponseDetailSchema[list[HistoryDetailSchema], HistoryMetadata],
)
async def get_account_history(
    history_service: HistoryServiceDep,
    account_id: str,
    user_id: str,
    user: UserDep,
    schema: GetHistorySchema = Depends(),
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
            account_id=account_id, interval=schema.interval
        )
    )

    return BaseResponseDetailSchema(
        detail=[HistoryDetailSchema.from_model(row) for row in history],
        message="История аккаунта успешно получена",
        metadata=(HistoryMetadata(**history_service.metadata)),
    )
