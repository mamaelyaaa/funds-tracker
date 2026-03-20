from fastapi import status

from core.exceptions import AppException


class UserAlreadyExistsException(AppException):
    status_code: int = status.HTTP_409_CONFLICT
    suggestion: str = "Попробуйте другой юзернейм"

    @property
    def message(self) -> str:
        return f"Пользователь с таким юзернеймом уже существует"


class PasswordsDontMatchesException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Попробуйте еще раз"

    @property
    def message(self) -> str:
        return f"Пароли должны совпадать"


class IncorrectPasswordException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Попробуйте еще раз"

    @property
    def message(self) -> str:
        return f"Неправильный пароль"
