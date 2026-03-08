from fastapi import status

from core.exceptions import AppException


class InvalidPercentException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Проценты должны быть от 0 до 100"

    @property
    def message(self) -> str:
        return "Выбран некорректный процент для вашей цели"


class FundNotFoundException(AppException):
    status_code: int = status.HTTP_404_NOT_FOUND
    suggestion: str = "Плохо все, че сказать, брокер не работает"

    @property
    def message(self) -> str:
        return "Накопленный остаток отсутствует"
