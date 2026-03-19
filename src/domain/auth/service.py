from dataclasses import dataclass

from domain.users.entity import User
from domain.users.protocols import UserRepositoryProtocol
from domain.users.values import Username
from .commands import RegisterUserCommand
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

    async def register_user(self, command: RegisterUserCommand) -> BearerToken:
        """Регистрация пользователя в системе"""

        exists_user = await self.user_repo.find_one(username=command.username)

        if exists_user:
            raise

        user: User = User(
            username=Username(command.username),
            password=self.secret_service.hash(command.password),
        )

        await self.user_repo.save(user)

        access_token = self.jwt_service.create_access_token(
            uid=user.id.value(),
            scope=[...],
        )

        return BearerToken(access_token=access_token, refresh_token="")

    async def login_user(self) -> BearerToken:
        """Логинит пользователя"""

        # if not self.secret_service.verify(
        #     password=command.password, hashed_password=exists_user.password
        # ):
        #     raise
        pass

    async def get_current_user(self):
        pass
