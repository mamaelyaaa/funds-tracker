from typing import Annotated

from fastapi import Depends, Path

from domain.users.entity import User
from domain.users.service import UserService
from infra import SessionDep
from infra.repositories.users import SQLAlchemyUserRepository


def get_user_service(session: SessionDep) -> UserService:
    return UserService(user_repo=SQLAlchemyUserRepository(session))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_user(user_service: UserServiceDep, user_id: str = Path()) -> User:
    user = await user_service.get_user_by_user_id(user_id)
    return user


UserDep = Annotated[User, Depends(get_user)]
