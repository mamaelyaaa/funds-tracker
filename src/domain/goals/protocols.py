from typing import Protocol

from domain.protocol import SQLAlchemyRepositoryProtocol
from .entities import Goal


class GoalRepositoryProtocol(SQLAlchemyRepositoryProtocol[Goal], Protocol):
    """Протокол репозитория целей пользователя"""

    async def is_title_taken(self, title: str, user_id: str) -> bool: ...

    async def count(self) -> int: ...

    async def count_by_user_id(self, user_id: str) -> int: ...

    async def check_exists_by_id(self, user_id: str, account_id: str) -> bool: ...
