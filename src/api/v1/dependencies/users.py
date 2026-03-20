from typing import Annotated

from fastapi import Depends

from domain.users.service import UserService
from infra import SessionDep
from infra.repositories.users import SQLAlchemyUserRepository


def get_user_service(session: SessionDep) -> UserService:
    return UserService(
        user_repo=SQLAlchemyUserRepository(session),
    )


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
