from fastapi import Path

from users.domain import User
from users.service import UserServiceDep
from users.values import UserId


async def get_user(
    user_service: UserServiceDep,
    user_id: str = Path(),
) -> User:
    user = await user_service.get_user_by_user_id(UserId(user_id))
    return user
