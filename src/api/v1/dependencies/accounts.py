from typing import Annotated

from fastapi import Depends, Path

from api.v1.dependencies.auth import AccessTokenDep
from domain.accounts.commands import GetAccountCommand
from domain.accounts.entities import Account
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


async def get_account(
    account_service: AccountServiceDep,
    user_id: AccessTokenDep,
    account_id: str = Path(),
) -> Account:
    account = await account_service.find_account_by_id(
        command=GetAccountCommand(
            account_id=account_id,
            user_id=user_id,
        )
    )
    return account


AccountDep = Annotated[Account, Depends(get_account)]
