from fastapi import status

from core.exceptions import AppException


class InvalidTokenException(AppException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    suggestion: str = "Убедитесь, что токен написан правильно"

    @property
    def message(self) -> str:
        return f"Невалидный токен доступа"


class MissingAccessTokenException(AppException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    suggestion: str = (
        "Добавьте в заголовок запроса токен доступа: Authorization: Bearer <>"
    )

    @property
    def message(self) -> str:
        return f"Отсутствует токен доступа"


class MissingRefreshTokenException(AppException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    suggestion: str = "Авторизуйтесь заново"

    @property
    def message(self) -> str:
        return f"Отсутствует токен обновления"


class TokenExpiredException(AppException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    suggestion: str = "Обновите токен доступа с помощью токена обновления"

    @property
    def message(self) -> str:
        return f"Токен доступа больше не валиден"


class RefreshNotFoundException(AppException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    suggestion: str = "Убедитесь что fingerprint корректен, или авторизуйтесь заново"

    @property
    def message(self) -> str:
        return f"Токен обновления не найден"
