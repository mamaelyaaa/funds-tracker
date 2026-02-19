import logging
from datetime import datetime, UTC, timedelta
from typing import Optional, Annotated

from dateutil.relativedelta import relativedelta
from fastapi import Depends

from domain.accounts.values import AccountId
from infra.repositories.histories import HistoryRepositoryDep
from .commands import (
    SaveHistoryCommand,
    GetAccountHistoryCommand,
)
from .dto import HistoryDTO
from .entities import History
from .exceptions import HistoryNotExistsException
from .protocols import HistoryRepositoryProtocol
from .values import HistoryInterval, HistoryPeriod

logger = logging.getLogger(__name__)


class HistoryService:

    INTERVALS: dict[HistoryInterval, datetime] = {
        HistoryInterval.MONTH1: datetime.now(UTC) - relativedelta(months=1),
        HistoryInterval.MONTH6: datetime.now(UTC) - relativedelta(months=6),
        HistoryInterval.YEAR: datetime.now(UTC) - relativedelta(years=1),
        HistoryInterval.ALL_TIME: datetime(2000, 1, 1),
    }
    PERIOD: dict[HistoryInterval, HistoryPeriod] = {
        HistoryInterval.MONTH1: HistoryPeriod.DAYS,
        HistoryInterval.MONTH6: HistoryPeriod.WEEKS,
        HistoryInterval.YEAR: HistoryPeriod.MONTHS,
        HistoryInterval.ALL_TIME: HistoryPeriod.YEARS,
    }

    def __init__(self, history_repo: HistoryRepositoryProtocol):
        self._repository = history_repo
        self.metadata: Optional[dict] = None

    async def save_account_history(self, command: SaveHistoryCommand) -> str:
        # Проверяем, была ли недавняя запись
        existing = await self._repository.get_acc_by_acc_id_with_time_limit(
            account_id=command.account_id,
            time_limit=timedelta(minutes=10),
        )

        if existing:
            logger.info(f"Обновляем историю #{existing.id.as_generic_type()}")

            updated_history = History(
                id=existing.id,
                account_id=AccountId(command.account_id),
                balance=command.balance,
            )

            upd_history = await self._repository.update(
                history_id=existing.id.as_generic_type(),
                upd_data=HistoryDTO.from_entity_to_dict(
                    updated_history, excludes=["id"]
                ),
            )
            return upd_history.id.as_generic_type()

        new_history = History.create(
            account_id=command.account_id,
            balance=command.balance,
        )

        history_id = await self._repository.save(new_history)
        logger.info(f"Создана новая история #{history_id}")

        return history_id

    async def get_account_history(
        self, command: GetAccountHistoryCommand
    ) -> list[History]:

        period, start_date = await self.set_metadata(command)

        history = await self._repository.get_history_linked_to_period(
            account_id=command.account_id,
            period=period,
            start_date=start_date,
        )
        return history

    async def get_history_percent_change(
        self, command: GetAccountHistoryCommand
    ) -> float:
        period, start_date = await self.set_metadata(command)

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

        divider = first_history.balance if first_history.balance != 0 else 1
        return (last_history.balance - first_history.balance) / divider

    async def set_metadata(self, command) -> tuple[str, datetime]:
        start_date: datetime = self.INTERVALS[command.interval]
        period: str = self.PERIOD[command.interval]
        self.metadata = {
            "start_date": start_date,
            "period": period,
        }
        return period, start_date


def get_history_service(histories_repo: HistoryRepositoryDep) -> HistoryService:
    return HistoryService(histories_repo)


HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
