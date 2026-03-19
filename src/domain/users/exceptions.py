from fastapi import status

from core.exceptions import AppException


class UserNotFoundException(AppException):
    status_code: int = status.HTTP_404_NOT_FOUND
    suggestion: str = "Проверьте правильность uuid пользователя"

    @property
    def message(self) -> str:
        return f"Пользователь не найден"


class TooLargeUsernameException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Сократите юзернейм до 31 символа"

    @property
    def message(self) -> str:
        return f"Слишком длинный юзернейм"
