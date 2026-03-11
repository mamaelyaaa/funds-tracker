from fastapi import status

from core.exceptions import AppException


class InvalidGoalDeadlineException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Дата не может быть раньше текущего времени"

    @property
    def message(self) -> str:
        return f"Выбрана некорректная дата окончания цели"


class GoalTitleAlreadyTakenException(AppException):
    status_code: int = status.HTTP_409_CONFLICT
    suggestion: str = "Попробуйте другое название"

    @property
    def message(self) -> str:
        return f"Цель с таким названием уже существует"


class GoalNotFoundException(AppException):
    status_code: int = status.HTTP_404_NOT_FOUND
    suggestion: str = "Проверьте id цели"

    @property
    def message(self) -> str:
        return f"Такая цель не найдена"
