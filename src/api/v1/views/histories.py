from typing import Annotated

from fastapi import APIRouter, Depends

from api.schemas import BaseResponseDetailSchema, PaginationSchema
from api.v1.schemas.histories import HistoryDetailSchema
from domain.commands import PaginationCommand
from domain.histories.commands import GetAccountHistoryCommand
from domain.histories.service import HistoryService, get_history_service
from domain.users.dependencies import UserDep

router = APIRouter(
    prefix="/users/{user_id}/accounts/{account_id}",
    tags=["История аккаунта⌚"],
)

HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]


@router.get(
    "/history",
    response_model=BaseResponseDetailSchema[
        list[HistoryDetailSchema], PaginationSchema
    ],
)
async def get_account_history(
    history_service: HistoryServiceDep,
    account_id: str,
    user_id: str,
    user: UserDep,
    pagination: PaginationCommand = Depends(),
):
    history = await history_service.get_account_history(
        command=GetAccountHistoryCommand(account_id=account_id, pagination=pagination)
    )

    return BaseResponseDetailSchema(
        detail=[HistoryDetailSchema.from_model(row) for row in history],
        message="История аккаунта успешно получена",
        metadata=PaginationSchema(page=pagination.page, limit=pagination.limit),
    )
