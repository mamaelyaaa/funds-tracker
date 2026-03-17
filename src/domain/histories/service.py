import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from core.settings import settings
from domain.accounts.values import AccountId
from domain.values import Money
from infra.database.specification import (
    PaginationSpecification,
    OrderBySpecification,
    DateRangeSpecification,
    TimeTruncSpecification,
)
from infra.models import HistoryModel
from .commands import (
    SaveHistoryCommand,
    GetAccountHistoryCommand,
)
from .entities import History
from .protocols import HistoryRepositoryProtocol
from .values import HistoryId

logger = logging.getLogger("history.service")


@dataclass(frozen=True)
class HistoryMetadata:
    start_date: datetime
    period: str


class HistoryService:

    def __init__(self, history_repo: HistoryRepositoryProtocol):
        self._history_repo = history_repo

    async def save_account_history(self, command: SaveHistoryCommand) -> str:
        """Сохраняем историю счёта"""

        last_history = await self._history_repo.find_one(
            PaginationSpecification(limit=1, offset=0),
            OrderBySpecification(field="created_at", direction="desc"),
            account_id=command.account_id,
        )

        if last_history:
            delta = command.balance - last_history.balance.to_float()
        else:
            delta = command.balance

        new_history = History(
            account_id=AccountId(command.account_id),
            balance=Money(command.balance),
            delta=delta,
            is_monthly_closing=command.is_monthly_closing,
            created_at=command.created_at,
        )

        history_id = await self._history_repo.save(new_history)
        logger.info(f"Создана новая история #%s", HistoryId(history_id).short)

        return history_id

    async def get_account_history(
        self, command: GetAccountHistoryCommand
    ) -> tuple[list[History], HistoryMetadata]:
        """Получение истории счета по периодам"""

        period = settings.db.sqla.period(command.interval)
        start_date = settings.db.sqla.start_date(command.interval)

        history = await self._history_repo.find_all(
            DateRangeSpecification(model=HistoryModel, start=start_date),
            TimeTruncSpecification(model=HistoryModel, period=period),
            OrderBySpecification(field="created_at", direction="asc"),
            account_id=command.account_id,
        )
        return history, HistoryMetadata(start_date=start_date, period=period)

    async def get_history_profit(
        self, command: GetAccountHistoryCommand
    ) -> dict[str, Any]:
        """Получение дохода по истории"""

        # first_history, *_ = await self._repository.get_history_linked_to_period(
        #     command.account_id,
        #     period,
        #     start_date,
        #     PaginationSpecification(offset=0, limit=1),
        #     OrderBySpecification(field="created_at", direction=False),
        # )
        # if not first_history:
        #     raise HistoryNotExistsException
        #
        # last_history, *_ = await self._repository.get_history_linked_to_period(
        #     command.account_id,
        #     period,
        #     start_date,
        #     PaginationSpecification(offset=0, limit=1),
        #     OrderBySpecification(field="created_at", direction=False),
        # )
        # if not last_history:
        #     raise HistoryNotExistsException

        # divider = (
        #     first_history.balance.as_generic_type() if first_history.balance != 0 else 1
        # )
        # percent_profit = (
        #     amount := last_history.balance.as_generic_type()
        #     - first_history.balance.as_generic_type()
        # ) / divider

        return {"percent_profit": percent_profit, "amount_profit": amount}
