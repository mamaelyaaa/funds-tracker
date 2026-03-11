from typing import Annotated

from fastapi import Depends

from domain.accounts.service import AccountService
from infra import SessionDep
from infra.publishers.accounts import AccountTaskiqPublisher
from infra.repositories.accounts import SQLAlchemyAccountRepository


def get_account_service(session: SessionDep) -> AccountService:
    return AccountService(
        account_repo=SQLAlchemyAccountRepository(session),
        account_publisher=AccountTaskiqPublisher(),
    )


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
