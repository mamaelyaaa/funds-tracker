class AppException(Exception):
    """Базовый класс ошибок приложения"""

    status_code: int
    suggestion: str

    @property
    def message(self) -> str:
        return "Ошибка приложения"
