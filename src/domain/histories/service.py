import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

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
    GetHistoryCommand,
)
from .entities import History
from .protocols import HistoryRepositoryProtocol
from .values import HistoryId

logger = logging.getLogger("history.service")


@dataclass(frozen=True)
class HistoryMetadata:
    start_date: datetime
    period: str


@dataclass(frozen=True)
class HistoryProfit:
    percent_profit: float
    amount_profit: float


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
            delta = command.balance - float(last_history.balance)
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

    async def get_account_history(self, command: GetHistoryCommand) -> tuple[
        list[History],
        HistoryProfit,
        HistoryMetadata,
    ]:
        """Получение истории счета по периодам"""

        period = settings.db.sqla.period(command.interval)
        start_date = settings.db.sqla.start_date(command.interval)

        history = await self._history_repo.find_all(
            DateRangeSpecification(model=HistoryModel, start=start_date),
            TimeTruncSpecification(model=HistoryModel, period=period),
            OrderBySpecification(field="created_at", direction="asc"),
            account_id=command.account_id,
        )

        last_history, first_history = history[-1], history[0]
        amount_profit = last_history.balance - first_history.balance

        percent_profit = (
            (last_history.balance - first_history.balance) / first_history.balance * 100
        )
        percent_profit = Decimal(str(percent_profit))
        percent_profit = percent_profit.quantize(exp=Decimal("1.00"))

        return (
            history,
            HistoryProfit(
                percent_profit=float(percent_profit),
                amount_profit=float(amount_profit),
            ),
            HistoryMetadata(start_date=start_date, period=period),
        )
