import logging
from datetime import datetime, UTC
from typing import Optional, Annotated, Any

from dateutil.relativedelta import relativedelta
from fastapi import Depends

from infra.repositories.histories import HistoryRepositoryDep
from .commands import (
    SaveHistoryCommand,
    GetAccountHistoryCommand,
)
from .entities import History
from .exceptions import HistoryNotExistsException
from .protocols import HistoryRepositoryProtocol
from .values import HistoryInterval, HistoryPeriod

logger = logging.getLogger(__name__)

INTERVALS: dict[HistoryInterval, datetime] = {
    HistoryInterval.DAY: datetime.now(UTC) - relativedelta(days=1),
    HistoryInterval.WEEK1: datetime.now(UTC) - relativedelta(weeks=1),
    HistoryInterval.MONTH1: datetime.now(UTC) - relativedelta(months=1),
    HistoryInterval.MONTH6: datetime.now(UTC) - relativedelta(months=6),
    HistoryInterval.YEAR: datetime.now(UTC) - relativedelta(years=1),
    HistoryInterval.ALL_TIME: datetime(2000, 1, 1),
}

PERIOD: dict[HistoryInterval, HistoryPeriod] = {
    HistoryInterval.DAY: HistoryPeriod.MINUTES,
    HistoryInterval.WEEK1: HistoryPeriod.HOURS,
    HistoryInterval.MONTH1: HistoryPeriod.DAYS,
    HistoryInterval.MONTH6: HistoryPeriod.WEEKS,
    HistoryInterval.YEAR: HistoryPeriod.MONTHS,
    HistoryInterval.ALL_TIME: HistoryPeriod.YEARS,
}


class HistoryService:

    def __init__(self, history_repo: HistoryRepositoryProtocol):
        self._repository = history_repo
        self.metadata: Optional[dict] = None

    async def save_account_history(self, command: SaveHistoryCommand) -> str:
        """Сохраняем историю счёта"""

        new_history = History.create(
            account_id=command.account_id,
            balance=command.balance,
            delta=command.delta,
        )

        history_id = await self._repository.save(new_history)
        logger.info(f"Создана новая история #{history_id}")

        return history_id

    async def get_account_history(
        self, command: GetAccountHistoryCommand
    ) -> list[History]:

        period, start_date = self.set_metadata(command)

        history = await self._repository.get_history_linked_to_period(
            account_id=command.account_id,
            period=period,
            start_date=start_date,
        )
        return history

    async def get_history_profit(
        self, command: GetAccountHistoryCommand
    ) -> dict[str, Any]:
        """Получение дохода по истории"""

        period, start_date = self.set_metadata(command)

        first_history, *_ = await self._repository.get_history_linked_to_period(
            account_id=command.account_id,
            start_date=start_date,
            period=period,
            limit=1,
            asc=True,
        )
        if not first_history:
            raise HistoryNotExistsException

        last_history, *_ = await self._repository.get_history_linked_to_period(
            account_id=command.account_id,
            start_date=start_date,
            period=period,
            limit=1,
            asc=False,
        )
        if not last_history:
            raise HistoryNotExistsException

        divider = (
            first_history.balance.as_generic_type() if first_history.balance != 0 else 1
        )
        percent_profit = (
            amount := last_history.balance.as_generic_type()
            - first_history.balance.as_generic_type()
        ) / divider

        return {"percent_profit": percent_profit, "amount_profit": amount}

    def set_metadata(self, command) -> tuple[str, datetime]:
        start_date: datetime = INTERVALS[command.interval]
        period: str = PERIOD[command.interval]
        self.metadata = {
            "start_date": start_date,
            "period": period,
        }
        return period, start_date


def get_history_service(histories_repo: HistoryRepositoryDep) -> HistoryService:
    return HistoryService(histories_repo)


HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
