from typing import Annotated

from fastapi import Depends

from domain.goals.service import GoalService
from infra import SessionDep
from infra.repositories.goals import SQLAlchemyGoalRepository


def get_goal_service(session: SessionDep) -> GoalService:
    return GoalService(
        goals_repo=SQLAlchemyGoalRepository(session),
    )


GoalServiceDep = Annotated[GoalService, Depends(get_goal_service)]
