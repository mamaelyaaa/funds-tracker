from typing import Annotated

from fastapi import Depends

from domain.funds.service import FundService
from domain.funds.use_case import FundDistUseCase
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


def get_fund_dist_use_case(
    fund_service: FundServiceDep,
    session: SessionDep,
) -> FundDistUseCase:
    from .accounts import get_account_service
    from .goals import get_goal_service

    return FundDistUseCase(
        fund_service=fund_service,
        account_service=get_account_service(session),
        goal_service=get_goal_service(session),
    )


FundDistUseCaseDep = Annotated[FundDistUseCase, Depends(get_fund_dist_use_case)]
