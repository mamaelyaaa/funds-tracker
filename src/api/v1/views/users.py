from fastapi import APIRouter, Depends
from fastapi.responses import Response
from fastapi.security import HTTPBearer

from api.schemas import BaseResponseDetailSchema
from api.v1.dependencies.auth import AuthServiceDep, AccessDepends, http_bearer
from api.v1.dependencies.users import UserServiceDep
from api.v1.schemas.users import (
    RegisterUserSchema,
    BearerTokenSchema,
    LoginUserSchema,
    UserDetailSchema,
)
from domain.auth.commands import RegisterUserCommand, LoginUserCommand

router = APIRouter(
    prefix="/users",
    tags=["Пользователи👥"],
)


@router.post("/register", response_model=BearerTokenSchema)
async def register_user(
    auth_service: AuthServiceDep,
    schema: RegisterUserSchema,
    response: Response,
):
    """Регистрация пользователя в системе"""

    bearer_tokens = await auth_service.register_user(
        command=RegisterUserCommand(
            username=schema.username,
            password=schema.password.get_secret_value(),
            password_repeat=schema.password_repeat.get_secret_value(),
        ),
        response=response,
    )
    return bearer_tokens


@router.post("/login", response_model=BearerTokenSchema)
async def login_user(
    auth_service: AuthServiceDep,
    schema: LoginUserSchema,
    response: Response,
):
    """Авторизация пользователя в системе"""

    bearer_tokens = await auth_service.login_user(
        command=LoginUserCommand(
            username=schema.username,
            password=schema.password.get_secret_value(),
        ),
        response=response,
    )
    return bearer_tokens


@router.get(
    "/me",
    dependencies=[Depends(http_bearer)],
    response_model=BaseResponseDetailSchema[UserDetailSchema, dict],
)
async def get_current_user(
    user_service: UserServiceDep,
    token: AccessDepends,
):
    """Авторизация пользователя в системе"""
    user = await user_service.get_user_by_user_id(user_id=token.sub)
    return BaseResponseDetailSchema(
        detail=user,
        message="Авторизованный пользователь успешно получен",
        metadata={},
    )
