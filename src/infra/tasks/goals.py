from typing import Annotated

from taskiq import TaskiqDepends

from domain.accounts.commands import GetAccountCommand
from domain.accounts.service import AccountService, get_account_service
from domain.goals.events import GoalLinkedToAccountEvent
from domain.goals.protocols import GoalsRepositoryProtocol
from infra import broker
from infra.repositories.goals import get_goals_repository


@broker.task(retry_on_error=True, max_retries=5)
async def goal_linked_to_account(
    event: GoalLinkedToAccountEvent,
    account_service: Annotated[AccountService, TaskiqDepends(get_account_service)],
    # goals_service: Annotated[GoalsService, TaskiqDepends(get_goals_service)],
    goal_repo: Annotated[GoalsRepositoryProtocol, TaskiqDepends(get_goals_repository)],
) -> float:

    account = await account_service.find_account_by_id(
        command=GetAccountCommand(account_id=event.account_id, user_id=event.user_id)
    )
    await goal_repo.save()
    # await goals_service.update_goal_partially(
    #     command=UpdateGoalPartiallyCommand(
    #         current_amount=account.balance, goal_id=event.goal_id, user_id=event.user_id
    #     )
    # )
    return account.balance
