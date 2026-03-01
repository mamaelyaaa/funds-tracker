from fastapi import status

from core.exceptions import AppException


class InvalidPercentException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Проценты должны быть от 0 до 100"

    @property
    def message(self) -> str:
        return f"Выбран некорректный процент для вашей цели"
