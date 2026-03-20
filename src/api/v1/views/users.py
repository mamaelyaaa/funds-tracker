from fastapi import Depends, APIRouter, Body
from starlette import status
from starlette.responses import Response

from api.schemas import BaseResponseDetailSchema, BaseExceptionSchema
from api.v1.dependencies.auth import http_bearer, AccessTokenDep, AuthServiceDep
from api.v1.dependencies.users import UserServiceDep
from api.v1.schemas.users import UserDetailSchema

router = APIRouter(prefix="/users", tags=["Пользователи👥"])


@router.get(
    "/me",
    dependencies=[Depends(http_bearer)],
    response_model=BaseResponseDetailSchema[UserDetailSchema, dict],
)
async def get_current_user(
    user_service: UserServiceDep,
    user_id: AccessTokenDep,
):
    """Авторизация пользователя в системе"""
    user = await user_service.get_user_by_user_id(user_id=user_id)
    return BaseResponseDetailSchema(
        detail=user,
        message="Авторизованный пользователь успешно получен",
        metadata={},
    )


@router.delete(
    "/logout",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": BaseExceptionSchema,
            "description": "Пользователь не авторизован",
        },
    },
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(http_bearer)],
)
async def logout_user(
    auth_service: AuthServiceDep,
    user_id: AccessTokenDep,
    response: Response,
    fingerprint: str = Body(embed=True),
):
    """Выход из системы пользователя"""
    await auth_service.logout_user(
        user_id=user_id, fingerprint=fingerprint, response=response
    )
    return


@router.delete(
    "/revoke-all",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": BaseExceptionSchema,
            "description": "Пользователь не авторизован",
        },
    },
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(http_bearer)],
)
async def revoke_user_sessions(
    auth_service: AuthServiceDep,
    user_id: AccessTokenDep,
    response: Response,
):
    """Выход из всех входов пользователя"""

    await auth_service.revoke_user_sessions(user_id=user_id, response=response)
    return
