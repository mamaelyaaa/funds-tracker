from fastapi import status

from core.exceptions import AppException


class UserNotFoundException(AppException):
    status_code: int = status.HTTP_404_NOT_FOUND
    suggestion: str = "Проверьте правильность uuid пользователя"

    @property
    def message(self) -> str:
        return f"Пользователь не найден"
