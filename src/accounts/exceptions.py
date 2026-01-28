from fastapi import status

from core.exceptions import AppException


class AccountNotFoundException(AppException):
    status_code: int = status.HTTP_404_NOT_FOUND
    suggestion: str = "Проверьте правильность uuid счёта"

    @property
    def message(self) -> str:
        return f"Счет не найден"
