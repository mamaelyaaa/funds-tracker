from typing import Annotated

from fastapi import Depends

from domain.histories.service import HistoryService
from infra import SessionDep
from infra.repositories.histories import SQLAlchemyHistoryRepository


def get_history_service(session: SessionDep) -> HistoryService:
    return HistoryService(
        history_repo=SQLAlchemyHistoryRepository(session),
    )


HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
