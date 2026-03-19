from typing import Annotated

from authx import TokenPayload
from fastapi import Depends, Path

from domain.auth.service import AuthService
from domain.users.entity import User
from domain.users.service import UserService
from infra import SessionDep
from infra.auth.authx import auth
from infra.auth.secrets import BcryptService
from infra.auth.tokens import TokenService
from infra.repositories.users import SQLAlchemyUserRepository


def get_user_service(session: SessionDep) -> UserService:
    return UserService(user_repo=SQLAlchemyUserRepository(session))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(
        user_repo=SQLAlchemyUserRepository(session),
        secret_service=BcryptService(),
        jwt_service=TokenService(),
    )


async def get_current_user(
    token: Annotated[TokenPayload, Depends(auth.access_token_required)],
):
    pass


async def get_user(user_service: UserServiceDep, user_id: str = Path()) -> User:
    user = await user_service.get_user_by_user_id(user_id)
    return user


UserDep = Annotated[User, Depends(get_user)]
