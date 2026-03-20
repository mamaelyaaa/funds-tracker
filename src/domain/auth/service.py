from dataclasses import dataclass

import structlog
from fastapi.responses import Response

from core.settings import settings
from domain.users.entity import User
from domain.users.exceptions import UserNotFoundException
from domain.users.protocols import UserRepositoryProtocol
from domain.users.values import Username, UserId
from .commands import RegisterUserCommand, LoginUserCommand
from .exceptions import (
    UserAlreadyExistsException,
    PasswordsDontMatchesException,
    IncorrectPasswordException,
)
from .protocols import JWTServiceProtocol, SecretsServiceProtocol

logger = structlog.get_logger()


@dataclass(frozen=True)
class BearerTokens:
    access_token: str
    refresh_token: str


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
        self, command: RegisterUserCommand, response: Response
    ) -> BearerTokens:
        """Регистрация пользователя в системе"""

        if not command.password == command.password_repeat:
            raise PasswordsDontMatchesException

        exists_user = await self.user_repo.find_one(username=command.username)
        logger.info("Проверяем уникальность юзернейма ... ", username=command.username)

        if exists_user:
            logger.warning("Юзернейм '%s' уже занят", exists_user.username)
            raise UserAlreadyExistsException

        user: User = User(
            username=Username(command.username),
            password=self.secret_service.hash(command.password),
        )

        await self.user_repo.save(user, commit=False)
        logger.info("Пользователь успешно создан", user_id=user.id.short)

        access_token = self.jwt_service.create_access_token(
            uid=user.id,
            expiry=settings.jwt.access_expires_in,
        )
        refresh_token = self.jwt_service.create_refresh_token(
            uid=user.id,
            expiry=settings.jwt.refresh_expires_in,
        )

        await self.jwt_service.save_or_update_refresh(
            refresh=refresh_token, fingerprint=command.fingerprint
        )
        logger.info("Сессия пользователя сохранена", user_id=user.id.short)

        refresh_jti = self.jwt_service.get_refresh_jti(refresh_token)

        self.jwt_service.save_refresh_token_cookie(
            refresh_jti=self.jwt_service.get_refresh_jti(refresh_token),
            response=response,
        )

        return BearerTokens(access_token=access_token, refresh_token=refresh_jti)

    async def login_user(
        self, command: LoginUserCommand, response: Response
    ) -> BearerTokens:
        """Авторизация пользователя"""

        logger.info("Ищем пользователя ... ", username=command.username)

        exists_user = await self.user_repo.find_one(username=command.username)
        if not exists_user:
            logger.warning("Пользователь с юзернеймом '%s' не найден", command.username)
            raise UserNotFoundException

        logger.info("Сверяем пароли ...")

        if not self.secret_service.verify(
            password=command.password,
            hashed_password=exists_user.password,
        ):
            logger.warning("Неправильный пароль")
            raise IncorrectPasswordException

        access_token = self.jwt_service.create_access_token(
            uid=exists_user.id,
            expiry=settings.jwt.access_expires_in,
        )
        refresh_token = self.jwt_service.create_refresh_token(
            uid=exists_user.id,
            expiry=settings.jwt.refresh_expires_in,
        )

        await self.jwt_service.save_or_update_refresh(
            refresh=refresh_token, fingerprint=command.fingerprint
        )
        logger.info("Сессия пользователя сохранена", user_id=exists_user.id.short)

        refresh_jti = self.jwt_service.get_refresh_jti(refresh_token)

        self.jwt_service.save_refresh_token_cookie(
            refresh_jti=refresh_jti,
            response=response,
        )

        return BearerTokens(access_token=access_token, refresh_token=refresh_jti)

    async def refresh_tokens(
        self, user_id: str, fingerprint: str, response: Response
    ) -> BearerTokens:
        """Обновляет токен доступа с помощью токена обновления"""

        user_session = await self.jwt_service.get_refresh_token_by_fingerprint(
            user_id=user_id, fingerprint=fingerprint
        )
        logger.info(
            "Получаем активную сессию пользователя", user_id=UserId(user_id).short
        )

        access_token = self.jwt_service.create_access_token(
            uid=user_session.user_id,
            expiry=settings.jwt.access_expires_in,
        )
        refresh_token = self.jwt_service.create_refresh_token(
            uid=user_session.user_id,
            expiry=settings.jwt.refresh_expires_in,
        )
        logger.info("Генерируем новые токены ...")

        await self.jwt_service.save_or_update_refresh(
            refresh=refresh_token,
            fingerprint=fingerprint,
        )

        logger.info("Сессия пользователя обновлена", user_id=UserId(user_id).short)

        refresh_jti = self.jwt_service.get_refresh_jti(refresh_token)

        self.jwt_service.save_refresh_token_cookie(
            refresh_jti=refresh_jti,
            response=response,
        )
        return BearerTokens(access_token=access_token, refresh_token=refresh_jti)

    async def logout_user(
        self, user_id: str, fingerprint: str, response: Response
    ) -> None:
        """Выход из системы для пользователя"""

        await self.jwt_service.delete_refresh_token(
            user_id=user_id, fingerprint=fingerprint
        )
        logger.info(
            "Удаляем текущую сессию пользователя",
            user_id=UserId(user_id).short,
            fingerprint=fingerprint,
        )

        self.jwt_service.delete_refresh_token_cookie(response)
        logger.info("Сессия удалена")
        return

    async def revoke_user_sessions(self, user_id: str, response: Response) -> None:
        """Ревокация сессий пользователя"""

        logger.info(
            "Удаляем все сессии пользователя",
            user_id=UserId(user_id).short,
        )
        await self.jwt_service.delete_all_user_refresh_tokens(user_id=user_id)
        self.jwt_service.delete_refresh_token_cookie(response)
        logger.info("Сессии удалены")
        return
