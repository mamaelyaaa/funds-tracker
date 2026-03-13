from typing import Annotated

from fastapi import Depends

from domain.funds.service import FundService
from infra import SessionDep

from infra.repositories.accounts import SQLAlchemyAccountRepository
from infra.repositories.fund_distribution import SQLAlchemyFundDistRepository
from infra.repositories.funds import SQLAlchemyFundRepository
from infra.repositories.goals import SQLAlchemyGoalRepository
from infra.repositories.histories import SQLAlchemyHistoryRepository


def get_fund_service(session: SessionDep) -> FundService:
    return FundService(
        fund_repo=SQLAlchemyFundRepository(session),
        fund_dist_repo=SQLAlchemyFundDistRepository(session),
        history_repo=SQLAlchemyHistoryRepository(session),
        account_repo=SQLAlchemyAccountRepository(session),
        goal_repo=SQLAlchemyGoalRepository(session),
    )


FundServiceDep = Annotated[FundService, Depends(get_fund_service)]
