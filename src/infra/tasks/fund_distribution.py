from domain.funds.events import FundClosedEvent
from infra import broker


@broker.task(retry_on_error=True, max_retries=5)
async def distribute_user_fund_task(
    event: FundClosedEvent,
    # fund_service: Annotated[FundService, TaskiqDepends(get_fund_service)],
    # account_service: Annotated[AccountService, TaskiqDepends(get_account_service)],
    # goal_service: Annotated[GoalService, TaskiqDepends(get_goal_service)],
) -> None:
    """Обновляет балансы резервов по закрытому распределению остатка"""

    # fund_dists = await fund_service.get_distributions_by_fund_is(
    #     user_id=event.user_id, fund_id=event.fund_id
    # )
