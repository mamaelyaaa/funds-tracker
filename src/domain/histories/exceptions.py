from starlette import status

from core.exceptions import AppException


class HistoryNotExistsException(AppException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    suggestion: str = "Ошибка сохранения истории счёта"

    @property
    def message(self) -> str:
        return f"История счёта отсутствует"
