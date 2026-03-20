from fastapi import APIRouter, Body, status
from fastapi.responses import Response

from api.schemas import BaseResponseDetailSchema, BaseExceptionSchema
from api.v1.dependencies.auth import (
    AuthServiceDep,
    RefreshTokenDep,
)
from api.v1.schemas.users import (
    RegisterUserSchema,
    LoginUserSchema,
    TokenTypeMeta,
)
from domain.auth.commands import RegisterUserCommand, LoginUserCommand
from domain.auth.service import BearerTokens

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация🪪"],
)


@router.post(
    "/register",
    response_model=BaseResponseDetailSchema[BearerTokens, TokenTypeMeta],
    responses={
        status.HTTP_201_CREATED: {
            "model": BaseResponseDetailSchema[BearerTokens, TokenTypeMeta],
            "description": "Пользователь успешно зарегистрирован",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BaseExceptionSchema,
            "description": "Пароли должны совпадать",
        },
        status.HTTP_409_CONFLICT: {
            "model": BaseExceptionSchema,
            "description": "Пользователь таким юзернеймом уже существует",
        },
    },
    status_code=status.HTTP_201_CREATED,
)
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
            fingerprint=schema.fingerprint,
        ),
        response=response,
    )
    return BaseResponseDetailSchema(
        detail=bearer_tokens,
        metadata=TokenTypeMeta(),
        message="Пользователь успешно зарегистрирован",
    )


@router.post(
    "/login",
    response_model=BaseResponseDetailSchema[BearerTokens, TokenTypeMeta],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": BaseExceptionSchema,
            "description": "Неправильный пароль",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": BaseExceptionSchema,
            "description": "Пользователь не найден",
        },
    },
)
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
            fingerprint=schema.fingerprint,
        ),
        response=response,
    )
    return BaseResponseDetailSchema(
        detail=bearer_tokens,
        metadata=TokenTypeMeta(),
        message="Пользователь успешно зарегистрирован",
    )


@router.post(
    "/refresh",
    response_model=BaseResponseDetailSchema[BearerTokens, TokenTypeMeta],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": BaseExceptionSchema,
            "description": "Пользователь не авторизован",
        },
    },
)
async def refresh_token(
    auth_service: AuthServiceDep,
    user_id: RefreshTokenDep,
    response: Response,
    fingerprint: str = Body(embed=True),
):
    """Обновление токена доступа"""

    bearer_tokens = await auth_service.refresh_tokens(
        user_id=user_id,
        fingerprint=fingerprint,
        response=response,
    )
    return BaseResponseDetailSchema(
        detail=bearer_tokens,
        metadata=TokenTypeMeta(),
        message="Токен доступа успешно обновлен",
    )
