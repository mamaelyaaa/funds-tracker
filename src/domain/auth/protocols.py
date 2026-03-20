from datetime import datetime
from typing import Protocol

from fastapi.responses import Response

from domain.auth.entity import UserSession
from domain.protocol import SQLAlchemyRepositoryProtocol


class UserSessionRepositoryProtocol(
    SQLAlchemyRepositoryProtocol[UserSession], Protocol
):
    """Протокол репозитория для работы с сессиями пользователей"""

    async def delete_expired_by_user(
        self, user_id: str, expired_before: datetime, commit: bool = True
    ) -> None: ...


class JWTServiceProtocol(Protocol):

    def create_access_token(self, uid: str, *args, **kwargs) -> str: ...

    def create_refresh_token(self, uid: str, *args, **kwargs) -> str: ...

    async def save_or_update_refresh(self, refresh: str, fingerprint: str) -> None: ...

    def save_refresh_token_cookie(
        self, refresh_jti: str, response: Response
    ) -> None: ...

    def delete_refresh_token_cookie(self, response: Response) -> None: ...

    def get_refresh_jti(self, refresh: str) -> str: ...

    async def get_refresh_by_jti(self, refresh_jti: str) -> UserSession: ...

    async def get_refresh_token_by_fingerprint(
        self, user_id: str, fingerprint: str
    ) -> UserSession: ...

    async def delete_refresh_token(self, user_id: str, fingerprint: str) -> None: ...

    async def delete_all_user_refresh_tokens(self, user_id: str) -> None: ...


class SecretsServiceProtocol(Protocol):

    def hash(self, password: str) -> str: ...

    def verify(self, password: str, hashed_password: str) -> bool: ...
