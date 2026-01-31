from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from infra.database import db_helper


class UnitOfWork:

    def __init__(self, session_factory: type[AsyncSession]):
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None

    @asynccontextmanager
    async def start(self):
        self._session = self._session_factory()
        try:
            yield self

        except Exception as e:
            await self._session.rollback()
            raise e

        finally:
            await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()


uow = UnitOfWork(session_factory=db_helper.session_factory)
