from fastapi import status

from core.exceptions import AppException


class AccountNotFoundException(AppException):
    status_code: int = status.HTTP_404_NOT_FOUND
    suggestion: str = "Проверьте правильность uuid счёта"

    @property
    def message(self) -> str:
        return f"Счет не найден"


class TooManyAccountsForUserException(AppException):
    status_code: int = status.HTTP_409_CONFLICT
    suggestion: str = "Удалите ненужные и попробуйте еще раз"

    @property
    def message(self) -> str:
        return f"Превышен лимит активных счетов"


class AccountAlreadyCreatedException(AppException):
    status_code: int = status.HTTP_409_CONFLICT
    suggestion: str = "Попробуйте другое название для создания нового счёта"

    @property
    def message(self) -> str:
        return f"Счёт с таким названием уже существует"
