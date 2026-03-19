from datetime import datetime, timezone

from authx import TokenPayload
from authx.exceptions import MissingTokenError, JWTDecodeError
from fastapi import HTTPException, status
from fastapi.requests import Request

from core.settings import settings
from infra.auth.authx import auth
from infra.auth.exceptions import (
    InvalidTokenException,
    MissingTokenException,
    TokenExpiredException,
)


async def verify_access_token(request: Request) -> TokenPayload:
    """Проверяет валидность access токена"""

    try:
        token = await auth.get_access_token_from_request(request, locations=["headers"])

    except MissingTokenError:
        raise MissingTokenException

    try:
        payload = auth.verify_token(token)
        return payload

    except JWTDecodeError:
        try:
            payload = token.verify(key=settings.jwt.secret, verify_jwt=False)
            if payload.iat <= datetime.timestamp(datetime.now(timezone.utc)):
                raise TokenExpiredException

        except JWTDecodeError:
            raise InvalidTokenException

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
