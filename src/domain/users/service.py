import structlog

from .entity import User
from .exceptions import UserNotFoundException
from .protocols import UserRepositoryProtocol
from .values import UserId

logger = structlog.get_logger()


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, user_repo: UserRepositoryProtocol):
        self._repository = user_repo

    async def get_user_by_user_id(self, user_id: str) -> User:
        user = await self._repository.find_one(id=user_id)
        if not user:
            logger.warning("Пользователь #%s не найден", UserId(user_id).short)
            raise UserNotFoundException
        return user
