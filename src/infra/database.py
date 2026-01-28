from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.settings import settings


class SQLADatabaseHelper:

    def __init__(self, url: str, echo: bool):
        self._engine = create_async_engine(url=url, echo=echo)
        self._sessionmaker = async_sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    async def dispose(self):
        await self._engine.dispose()

    async def session_getter(self):
        async with self._sessionmaker.begin() as session:
            yield session


db_helper = SQLADatabaseHelper(
    url=str(settings.db.POSTGRES_DSN), echo=settings.db.sqla.echo
)

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_getter)]
