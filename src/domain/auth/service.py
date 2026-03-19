from dataclasses import dataclass

from fastapi.responses import Response

from domain.users.entity import User
from domain.users.exceptions import UserNotFoundException
from domain.users.protocols import UserRepositoryProtocol
from domain.users.values import Username
from .commands import RegisterUserCommand, LoginUserCommand
from .exceptions import (
    UserAlreadyExistsException,
    PasswordsDontMatchesException,
    IncorrectPasswordException,
)
from .protocols import JWTServiceProtocol, SecretsServiceProtocol


@dataclass(frozen=True)
class BearerToken:
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class AuthService:
    """Сервис авторизации и аутентификации пользователей"""

    def __init__(
        self,
        user_repo: UserRepositoryProtocol,
        jwt_service: JWTServiceProtocol,
        secret_service: SecretsServiceProtocol,
    ):
        self.user_repo = user_repo
        self.jwt_service = jwt_service
        self.secret_service = secret_service

    async def register_user(
        self,
        command: RegisterUserCommand,
        response: Response,
    ) -> BearerToken:
        """Регистрация пользователя в системе"""

        if not command.password == command.password_repeat:
            raise PasswordsDontMatchesException

        exists_user = await self.user_repo.find_one(username=command.username)

        if exists_user:
            raise UserAlreadyExistsException

        user: User = User(
            username=Username(command.username),
            password=self.secret_service.hash(command.password),
        )

        await self.user_repo.save(user)

        access_token = self.jwt_service.create_access_token(uid=user.id)
        refresh_token = self.jwt_service.create_refresh_token(uid=user.id)

        await self.jwt_service.save_or_update_refresh(refresh_token)

        self.jwt_service.save_refresh_token_cookie(
            refresh_jti=refresh_token,
            response=response,
        )

        return BearerToken(access_token=access_token, refresh_token=refresh_token)

    async def login_user(
        self,
        command: LoginUserCommand,
        response: Response,
    ) -> BearerToken:
        """Авторизовывает пользователя"""

        exists_user = await self.user_repo.find_one(username=command.username)
        if not exists_user:
            raise UserNotFoundException

        if not self.secret_service.verify(
            password=command.password,
            hashed_password=exists_user.password,
        ):
            raise IncorrectPasswordException

        access_token = self.jwt_service.create_access_token(uid=exists_user.id)
        refresh_token = await self.jwt_service.create_refresh_token(uid=exists_user.id)

        self.jwt_service.save_refresh_token_cookie(
            refresh_jti=refresh_token,
            response=response,
        )

        return BearerToken(access_token=access_token, refresh_token=refresh_token)

    async def get_current_user(self):
        pass
