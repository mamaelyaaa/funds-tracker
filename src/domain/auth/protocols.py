from typing import Protocol


class JWTServiceProtocol(Protocol):

    def create_access_token(
        self, uid: str, scope: list[str], *args, **kwargs
    ) -> str: ...

    def create_refresh_token(self, uid: str, *args, **kwargs) -> str: ...

    def save_refresh_token(self, refresh: str) -> None: ...


class SecretsServiceProtocol(Protocol):

    def hash(self, password: str) -> str: ...

    def verify(self, password: str, hashed_password: str) -> bool: ...
