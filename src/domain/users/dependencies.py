from typing import Annotated

from fastapi import Path, Depends

from .entity import User
from .service import UserServiceDep
from .values import UserId


async def get_user(
    user_service: UserServiceDep,
    user_id: str = Path(),
) -> User:
    user = await user_service.get_user_by_user_id(UserId(user_id))
    return user


UserDep = Annotated[User, Depends(get_user)]
