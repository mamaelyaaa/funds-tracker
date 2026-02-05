import logging
from datetime import datetime, UTC
from typing import Optional, Annotated

from asyncpg.pgproto.pgproto import timedelta
from dateutil.relativedelta import relativedelta
from fastapi import Depends

from domain.accounts.values import AccountId
from domain.histories.commands import (
    SaveHistoryCommand,
    GetAccountHistoryCommand,
)
from domain.histories.domain import History
from domain.histories.repository import HistoryRepositoryProtocol
from domain.histories.values import HistoryInterval, HistoryPeriod
from infra.repositories.histories import HistoryRepositoryDep

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
            account_id=AccountId(command.account_id),
            time_limit=timedelta(minutes=10),
        )

        if existing:
            logger.info(f"Обновляем историю #{existing.id.value}")

            updated_history = History(
                id=existing.id,
                account_id=AccountId(command.account_id),
                balance=command.balance,
            )

            upd_history = await self._repository.update(
                history_id=existing.id,
                new_history=updated_history,
            )
            return upd_history.id.value

        new_history = History(
            account_id=AccountId(command.account_id),
            balance=command.balance,
        )

        history_id = await self._repository.save(new_history)
        logger.info(f"Создана новая история #{history_id.value}")

        return history_id.value

    async def get_account_history(
        self, command: GetAccountHistoryCommand
    ) -> list[History]:

        start_date: datetime = self.INTERVALS[command.interval]
        period: str = self.PERIOD[command.interval]
        self.metadata = {
            "start_date": start_date,
            "period": period,
        }

        history = await self._repository.get_history_linked_to_period(
            account_id=AccountId(command.account_id),
            period=period,
            start_date=start_date,
        )
        return history


def get_history_service(histories_repo: HistoryRepositoryDep) -> HistoryService:
    return HistoryService(histories_repo)


HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
