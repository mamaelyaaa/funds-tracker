import logging
from functools import lru_cache
from typing import Annotated

from asyncpg import ConnectionDoesNotExistError
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

from core.settings import settings
from infra.exceptions import UnavailableDBException

logger = logging.getLogger(__name__)


class SQLADatabaseHelper:

    def __init__(self, url: str, echo: bool):
        self._engine = create_async_engine(url=url, echo=echo)
        self._session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    async def dispose(self):
        await self._engine.dispose()

    async def session_getter(self):
        async with self._session_factory() as session:
            try:
                yield session

            except (ConnectionDoesNotExistError, OSError):
                logger.error("Не удается подключиться к базе данных")
                raise UnavailableDBException

            finally:
                await session.close()

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory


db_helper = SQLADatabaseHelper(url=settings.db.POSTGRES_DSN, echo=settings.db.sqla.echo)
SessionDep = Annotated[AsyncSession, Depends(db_helper.session_getter)]
