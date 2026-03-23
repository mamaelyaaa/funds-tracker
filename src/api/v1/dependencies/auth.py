from datetime import datetime, timezone
from typing import Annotated

import structlog
from authx.exceptions import MissingTokenError, JWTDecodeError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from starlette import status
from starlette.requests import Request

from core.config import settings
from domain.auth.service import AuthService
from domain.users.values import UserId
from infra import SessionDep
from core.infra.authx import auth
from infra.auth.exceptions import (
    MissingAccessTokenException,
    TokenExpiredException,
    InvalidTokenException,
    MissingRefreshTokenException,
)
from infra.auth.secrets import BcryptService
from infra.auth.tokens import TokenService
from infra.repositories.user_sessions import SQLAlchemyUserSessionRepository
from infra.repositories.users import SQLAlchemyUserRepository

logger = structlog.get_logger()


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(
        user_repo=SQLAlchemyUserRepository(session),
        jwt_service=TokenService(SQLAlchemyUserSessionRepository(session)),
        secret_service=BcryptService(),
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

http_bearer = HTTPBearer(auto_error=False)


async def verify_access_token(request: Request) -> UserId:
    """Проверяет валидность токена доступа"""

    try:
        token = await auth.get_access_token_from_request(request, locations=["headers"])

    except MissingTokenError:
        logger.warning("Токен доступа не найден в заголовках")
        raise MissingAccessTokenException

    try:
        payload = auth.verify_token(token)
        return UserId(payload.sub)

    except JWTDecodeError:
        try:
            payload = token.verify(key=settings.jwt.secret, verify_jwt=False)
            if payload.iat <= datetime.timestamp(datetime.now(timezone.utc)):
                logger.warning(
                    "Время жизни токена доступа истекло", user_id=payload.sub
                )
                raise TokenExpiredException

        except JWTDecodeError:
            logger.warning("Невалидный токен доступа", token=token)
            raise InvalidTokenException

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


AccessTokenDep = Annotated[str, Depends(verify_access_token)]


async def verify_refresh_token(
    auth_service: AuthServiceDep, request: Request
) -> UserId:
    """Проверяет валидность токена обновления"""

    refresh_jti = request.cookies.get(settings.jwt.refresh_cookie_name)

    if not refresh_jti:
        logger.warning("Токен обновления не найден")
        raise MissingRefreshTokenException

    user_session = await auth_service.jwt_service.get_refresh_by_jti(
        refresh_jti=refresh_jti
    )

    if user_session.expires_in < datetime.now(timezone.utc):
        logger.warning(
            "Время жизни токена доступа истекло", user_id=user_session.user_id
        )
        raise TokenExpiredException

    return user_session.user_id


RefreshTokenDep = Annotated[str, Depends(verify_refresh_token)]
