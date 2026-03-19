import logging

from .entity import User
from .exceptions import UserNotFoundException
from .protocols import UserRepositoryProtocol
from .values import UserId

logger = logging.getLogger("user.service")


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, user_repo: UserRepositoryProtocol):
        self.user_repo = user_repo

    async def get_user_by_user_id(self, user_id: str) -> User:
        user = await self.user_repo.find_one(id=user_id)
        if not user:
            logger.warning("Пользователь #%s не найден", UserId(user_id).short)
            raise UserNotFoundException
        return user
