import logging
from typing import Annotated

from fastapi import Depends

from infra.repositories.users import UserRepositoryDep
from users.domain import User
from users.exceptions import UserNotFoundException
from users.repository import UserRepositoryProtocol
from users.values import UserId

logger = logging.getLogger(__name__)


class UserService:

    def __init__(self, user_repo: UserRepositoryProtocol):
        self._repository = user_repo

    async def get_user_by_user_id(self, user_id: UserId) -> User:
        user = await self._repository.get_by_id(user_id)
        if not user:
            logger.warning("Пользователь #%s не найден", user_id.value)
            raise UserNotFoundException
        return user


def get_user_service(user_repo: UserRepositoryDep) -> UserService:
    return UserService(user_repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
