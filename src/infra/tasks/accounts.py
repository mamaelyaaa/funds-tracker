import logging
from typing import Annotated

from taskiq import TaskiqDepends

from domain.accounts.events import (
    AccountCreatedEvent,
    FundCreatedEvent,
    BalanceUpdatedEvent,
    FundUpdatedEvent,
)
from domain.funds.service import (
    FundService,
    get_fund_service,
)
from domain.funds.commands import CreateFundCommand, UpdateFundCommand
from domain.histories.commands import SaveHistoryCommand
from domain.histories.service import get_history_service, HistoryService
from infra import broker

logger = logging.getLogger(__name__)


@broker.task(retry_on_error=True, max_retries=10)
async def save_account_history(
    event: AccountCreatedEvent | BalanceUpdatedEvent,
    history_service: Annotated[HistoryService, TaskiqDepends(get_history_service)],
) -> str:
    logger.info(f"Сохраняем историю счёта #{event.account_id[:8]} ...")

    history_id: str = await history_service.save_account_history(
        command=SaveHistoryCommand(
            balance=event.new_balance,
            account_id=event.account_id,
            user_id=event.user_id,
            delta=event.delta if isinstance(event, BalanceUpdatedEvent) else 0,
            is_monthly_closing=(
                event.is_monthly_closing
                if isinstance(event, BalanceUpdatedEvent)
                else False
            ),
        )
    )
    return history_id


@broker.task(retry_on_error=True, max_retries=3)
async def create_fund_task(
    event: FundCreatedEvent,
    fund_service: Annotated[FundService, TaskiqDepends(get_fund_service)],
):

    await fund_service.create_fund(
        command=CreateFundCommand(
            user_id=event.user_id, start_date=event.start_date, end_date=event.end_date
        )
    )
    logger.info(f"Создан накопительный остаток для пользователя #{event.user_id[:8]}")


@broker.task(retry_on_error=True, max_retries=3)
async def update_fund_task(
    event: FundUpdatedEvent,
    fund_service: Annotated[FundService, TaskiqDepends(get_fund_service)],
):

    await fund_service.update_fund(
        command=UpdateFundCommand(
            user_id=event.user_id, end_date=event.end_date, new_amount=event.new_balance
        )
    )
    logger.info(f"Накопительный остаток обновлен для пользователя #{event.user_id[:8]}")
