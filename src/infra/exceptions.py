from starlette import status

from core.exceptions import AppException


class UnavailableDBException(AppException):
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE
    suggestion: str = "Удостоверьтесь, что сервис активен и готов принимать запросы"

    @property
    def message(self) -> str:
        return f"Не удается подключиться к базе данных"
