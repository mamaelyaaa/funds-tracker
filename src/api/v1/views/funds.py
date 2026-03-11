from typing import Annotated

from fastapi import APIRouter, Depends

from api.schemas import BaseResponseDetailSchema
from api.v1.schemas.funds import FundDetailSchema
from domain.funds.dto import FundDTO
from domain.funds.service import FundService, get_fund_service
from domain.users.dependencies import get_user

router = APIRouter(
    prefix="/users/{user_id}/funds",
    tags=["Накопительный остаток 🫰"],
    dependencies=[Depends(get_user)],
)

FundServiceDep = Annotated[FundService, Depends(get_fund_service)]


@router.get("", response_model=BaseResponseDetailSchema[list[FundDetailSchema], dict])
async def get_user_distributed_funds(fund_service: FundServiceDep, user_id: str):
    funds = await fund_service.get_closed_funds(user_id)
    return BaseResponseDetailSchema(
        message="Получена история распределенных остатков пользователя",
        detail=[FundDTO.from_entity_to_dict(fund) for fund in funds],
        metadata={},
    )


@router.get("/current", response_model=BaseResponseDetailSchema[FundDetailSchema, dict])
async def get_last_open_fund(fund_service: FundServiceDep, user_id: str):
    fund = await fund_service.get_last_opened_fund(user_id)
    return BaseResponseDetailSchema(
        message="Накопительный остаток получен",
        detail=FundDTO.from_entity_to_dict(fund),
        metadata={},
    )


@router.post("/current/close", deprecated=True)
async def close_current_fund():
    pass
