from typing import Annotated

from fastapi import APIRouter, Depends

from api.schemas import BaseResponseDetailSchema
from api.v1.schemas.net_worth import NetWorthBalanceSchema
from domain.net_worth.service import NetWorthService, get_net_worth_service
from domain.users.dependencies import UserDep

router = APIRouter(prefix="/users/{user_id}", tags=["Капитал💹"])


NetWorthServiceDep = Annotated[NetWorthService, Depends(get_net_worth_service)]


@router.get(
    "/net-worth/total-balance",
    response_model=BaseResponseDetailSchema[NetWorthBalanceSchema, dict],
    deprecated=True,
)
async def get_user_net_worth_total_balance(
    nw_service: NetWorthServiceDep,
    user_id: str,
    user: UserDep,
):
    total_balance = await nw_service.calculate_total_balance(user_id=user.id)
    return BaseResponseDetailSchema(
        message="Получен капитал пользователя",
        detail=NetWorthBalanceSchema(total_balance=total_balance),
    )
