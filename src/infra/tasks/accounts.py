from datetime import datetime
from typing import Annotated

import structlog
from taskiq import TaskiqDepends

from api.v1.dependencies.funds import get_fund_service
from api.v1.dependencies.histories import get_history_service
from domain.accounts.events import AccountCreatedEvent, BalanceUpdatedEvent
from domain.accounts.entities import AccountId
from domain.funds.commands import CreateOrUpdateFundCommand
from domain.funds.service import FundService
from domain.histories.commands import SaveHistoryCommand
from domain.histories.service import HistoryService
from infra import broker

logger = structlog.get_logger()


@broker.task(retry_on_error=True, max_retries=3)
async def save_account_history(
    event: AccountCreatedEvent | BalanceUpdatedEvent,
    history_service: Annotated[HistoryService, TaskiqDepends(get_history_service)],
) -> str:
    logger.info("Сохраняем историю счёта #%s ...", AccountId(event.account_id).short)

    history_id: str = await history_service.save_account_history(
        command=SaveHistoryCommand(
            balance=float(event.new_balance),
            account_id=event.account_id,
            user_id=event.user_id,
            is_monthly_closing=(
                event.is_monthly_closing
                if isinstance(event, BalanceUpdatedEvent)
                else False
            ),
            created_at=event.occurred_at,
        )
    )
    return history_id


@broker.task(retry_on_error=True, max_retries=3)
async def create_or_update_user_fund_task(
    user_id: str,
    account_id: str,
    end_date: datetime,
    fund_service: Annotated[FundService, TaskiqDepends(get_fund_service)],
) -> str:
    fund_id = await fund_service.create_or_update_fund(
        command=CreateOrUpdateFundCommand(
            user_id=user_id, end_date=end_date, account_id=account_id
        )
    )
    return fund_id
