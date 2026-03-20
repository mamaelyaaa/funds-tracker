from fastapi import APIRouter, Depends
from starlette import status

from api.schemas import (
    BaseResponseDetailSchema,
    BaseResponseSchema,
    PaginationMetaSchema,
    PaginationDep,
    BaseExceptionSchema,
)
from api.v1.dependencies.auth import http_bearer, AccessTokenDep
from api.v1.dependencies.funds import FundServiceDep, FundDistUseCaseDep
from api.v1.schemas.funds import FundDetailSchema, FundCloseSchema
from domain.commands import PaginationCommand
from domain.funds.commands import (
    CreateReserveCommand,
    GetFundsCommand,
    CreateReservesCommand,
)
from domain.funds.dto import FundDTO

router = APIRouter(
    prefix="/funds",
    tags=["Накопительный остаток 🫰"],
    dependencies=[Depends(http_bearer)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": BaseExceptionSchema,
            "description": "Пользователь не авторизован",
        },
    },
)


@router.get(
    "",
    response_model=BaseResponseDetailSchema[
        list[FundDetailSchema], PaginationMetaSchema
    ],
)
async def get_user_distributed_funds(
    fund_service: FundServiceDep,
    user_id: AccessTokenDep,
    pagination: PaginationDep,
):
    """Получение всех накопительных остатков пользователя"""

    funds, pagination_meta = await fund_service.get_unopened_funds(
        command=GetFundsCommand(
            user_id=user_id,
            pagination=PaginationCommand(**pagination.model_dump()),
        )
    )
    return BaseResponseDetailSchema(
        message="Получена история распределенных остатков пользователя",
        detail=[FundDTO.from_entity_to_dict(fund) for fund in funds],
        metadata=pagination_meta,
    )


@router.get(
    "/current",
    response_model=BaseResponseDetailSchema[FundDetailSchema, dict],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": BaseExceptionSchema,
            "description": "Накопленный остаток отсутствует",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BaseExceptionSchema,
            "description": "Накопленный остаток уже был сегодня распределен",
        },
    },
)
async def get_last_open_fund(fund_service: FundServiceDep, user_id: AccessTokenDep):
    """Получение крайнего накопительного остатка пользователя"""

    fund = await fund_service.get_last_opened_fund(user_id)
    return BaseResponseDetailSchema(
        message="Накопительный остаток получен",
        detail=FundDTO.from_entity_to_dict(fund),
        metadata={},
    )


@router.post("/current/close", response_model=BaseResponseSchema)
async def close_current_fund(
    fund_dist_use_case: FundDistUseCaseDep,
    schema: FundCloseSchema,
    user_id: AccessTokenDep,
):
    """Распределение текущего накопленного остатка по резервам (счетам и целям)"""

    await fund_dist_use_case.close_head_fund(
        command=CreateReservesCommand(
            user_id=user_id,
            reserves=[
                CreateReserveCommand(**reserve.model_dump())
                for reserve in schema.reserves
            ],
        )
    )
    return BaseResponseSchema(message="Распределение остатка прошло успешно!")
