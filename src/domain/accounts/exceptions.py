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


class TooLargeTitleException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Попробуйте другое название"

    @property
    def message(self) -> str:
        return f"Слишком длинное название счёта"


class EmptyTitleException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Введите название для счёта"

    @property
    def message(self) -> str:
        return f"Название счёта не может быть пустым"


class InvalidLettersTitleException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = (
        "Попробуйте другое название. Используйте цифры, латиницу и кириллицу"
    )

    @property
    def message(self) -> str:
        return f"Невалидные символы для названия счёта"


class InvalidInitBalanceException(AppException):
    status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT
    suggestion: str = "Баланс должен быть не отрицательным"

    @property
    def message(self) -> str:
        return f"Невалидный первоначальный баланс для счёта"
