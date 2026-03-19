from typing import Annotated

from authx import TokenPayload
from fastapi import Depends
from fastapi.security import HTTPBearer

from domain.auth.service import AuthService
from infra import SessionDep
from infra.auth.secrets import BcryptService
from infra.auth.tokens import TokenService
from infra.auth.verify import verify_access_token
from infra.repositories.users import SQLAlchemyUserRepository


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(
        user_repo=SQLAlchemyUserRepository(session),
        jwt_service=TokenService(),
        secret_service=BcryptService(),
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

http_bearer = HTTPBearer(auto_error=False)

AccessDepends = Annotated[TokenPayload, Depends(verify_access_token)]
