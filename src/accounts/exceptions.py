from accounts.domain import AccountId
from core.exceptions import AppException
from fastapi import status


class AccountNotFoundException(AppException):
    """Счет не найден"""

    status_code: int = status.HTTP_404_NOT_FOUND
    suggestion: str = "Проверьте правильность uuid счёта"

    @property
    def message(self) -> str:
        return f"Счет не найден"
