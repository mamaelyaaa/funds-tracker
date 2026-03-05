from starlette import status

from core.exceptions import AppException


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


class InvalidBalanceException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Баланс должен быть не отрицательным"

    @property
    def message(self) -> str:
        return f"Невалидный первоначальный баланс для счёта"
