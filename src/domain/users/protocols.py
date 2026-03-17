from typing import Protocol

from domain.protocol import SQLAlchemyRepositoryProtocol
from .entity import User


class UserRepositoryProtocol(SQLAlchemyRepositoryProtocol[User], Protocol):
    """Протокол репозитория для работы с пользователями"""

    pass
