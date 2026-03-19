from typing import Protocol

from fastapi.responses import Response

from domain.auth.entity import UserSession
from domain.protocol import SQLAlchemyRepositoryProtocol


class UserSessionRepositoryProtocol(
    SQLAlchemyRepositoryProtocol[UserSession], Protocol
):
    """Протокол репозитория для работы с сессиями пользователей"""

    async def delete_many(
        self, sessions_ids: list[str], commit: bool = True, *specs, **filter_by
    ) -> None: ...


class JWTServiceProtocol(Protocol):

    def create_access_token(self, uid: str, *args, **kwargs) -> str: ...

    def create_refresh_token(self, uid: str, *args, **kwargs) -> str: ...

    async def save_or_update_refresh(self, refresh: str) -> None: ...

    def save_refresh_token_cookie(
        self, refresh_jti: str, response: Response
    ) -> None: ...


class SecretsServiceProtocol(Protocol):

    def hash(self, password: str) -> str: ...

    def verify(self, password: str, hashed_password: str) -> bool: ...
