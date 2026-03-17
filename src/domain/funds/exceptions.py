from fastapi import status

from core.exceptions import AppException


class InvalidPercentException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Проценты должны быть от 0 до 100"

    @property
    def message(self) -> str:
        return "Выбран некорректный процент для вашей цели"


class FundNotFoundException(AppException):
    status_code: int = status.HTTP_404_NOT_FOUND
    suggestion: str = "Обновите счёт с меткой 'Закрывающий месяц'"

    @property
    def message(self) -> str:
        return "Накопленный остаток отсутствует"


class FundAlreadyDistributedTodayException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Обновите счёт завтра с меткой 'Закрывающий месяц'"

    @property
    def message(self) -> str:
        return "Накопленный остаток уже был распределен сегодня"


class ReserveNotImplementedException(AppException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    suggestion: str = "Добавьте новый тип или убедитесь что введен правильный"

    @property
    def message(self) -> str:
        return "Неизвестный тип резерва для остатка"


class InvalidFundPercentageException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Перераспределите проценты, чтобы в сумме было 100"

    @property
    def message(self) -> str:
        return "Некорректное распределение остатка по процентам"


class InvalidFundDateException(AppException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    suggestion: str = "Дата начала отсчета должна быть не больше чем дата окончания"

    @property
    def message(self) -> str:
        return f"Некорректные даты для остатка"
