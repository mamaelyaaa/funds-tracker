from fastapi import status

from core.exceptions import AppException


class InvalidGoalPercentageException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Значение должно варьироваться от 0 до 1"

    @property
    def message(self) -> str:
        return f"Выбран некорректный процент для вашей цели"


class InvalidGoalDeadlineException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Дата не может быть раньше текущего времени"

    @property
    def message(self) -> str:
        return f"Выбрана некорректная дата окончания цели"


class InvalidGoalAmountsException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Цена не должна быть меньше 0"

    @property
    def message(self) -> str:
        return f"Некорректная цена цели"


class GoalTitleAlreadyTakenException(AppException):
    status_code: int = status.HTTP_409_CONFLICT
    suggestion: str = "Попробуйте другое название"

    @property
    def message(self) -> str:
        return f"Цель с таким названием уже существует"


class GoalNotFoundException(AppException):
    status_code: int = status.HTTP_404_NOT_FOUND
    suggestion: str = "Проверьте uid цели"

    @property
    def message(self) -> str:
        return f"Такой цели не существует"


class GoalsPercentageOutOfBoundsException(AppException):
    status_code: int = status.HTTP_409_CONFLICT
    suggestion: str = "Уменьшите проценты других счетов, чтобы добавить новую цель"

    @property
    def message(self) -> str:
        return f"Требуется повторное распределение процентов для целей"
