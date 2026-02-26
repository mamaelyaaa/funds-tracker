from typing import Annotated

from fastapi import APIRouter, Depends

from api.schemas import BaseResponseDetailSchema
from api.v1.schemas.net_worth import NetWorthBalanceSchema
from domain.histories.values import HistoryInterval
from domain.net_worth.commands import GetByIntervals
from domain.net_worth.service import NetWorthService, get_net_worth_service
from domain.users.dependencies import get_user

router = APIRouter(
    prefix="/users/{user_id}", tags=["Капитал💹"], dependencies=[Depends(get_user)]
)


NetWorthServiceDep = Annotated[NetWorthService, Depends(get_net_worth_service)]


@router.get(
    "/net-worth/total-balance",
    response_model=BaseResponseDetailSchema[NetWorthBalanceSchema, dict],
)
async def get_user_net_worth_total_balance(
    nw_service: NetWorthServiceDep, user_id: str
):
    total_balance = await nw_service.calculate_total_balance(user_id=user_id)
    return BaseResponseDetailSchema(
        message="Получен капитал пользователя",
        detail=NetWorthBalanceSchema(total_balance=total_balance),
        metadata={},
    )


@router.get(
    "/net-worth",
    # response_model=BaseResponseDetailSchema[NetWorthBalanceSchema, dict],
)
async def get_user_analysis(
    nw_service: NetWorthServiceDep, user_id: str, interval: HistoryInterval
):
    incomes = await nw_service.get_user_incomes_by_timeline(
        command=GetByIntervals(user_id=user_id, interval=interval)
    )
    expenses = await nw_service.get_user_expenses_by_timeline(
        command=GetByIntervals(user_id=user_id, interval=interval)
    )

    return {"incomes": incomes, "expenses": expenses}

    return BaseResponseDetailSchema(
        message="",
        detail=NetWorthBalanceSchema(total_balance=incomes),
        metadata={},
    )
