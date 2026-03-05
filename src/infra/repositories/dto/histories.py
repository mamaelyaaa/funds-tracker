from domain.accounts.values import AccountId
from domain.values import Money
from domain.histories.dto import HistoryDTO
from domain.histories.entities import History
from domain.histories.values import HistoryId
from infra.models import HistoryModel
from infra.repositories.dto.base import BaseOrmDTO


class HistoryOrmDTO(BaseOrmDTO, HistoryDTO):

    @staticmethod
    def from_orm_to_entity(model: HistoryModel) -> History:
        return History(
            id=HistoryId(model.id),
            account_id=AccountId(model.account_id),
            delta=float(model.delta),
            balance=Money(model.balance),
            is_monthly_closing=model.is_monthly_closing,
            created_at=HistoryOrmDTO._ensure_utc(model.created_at),
        )

    @staticmethod
    def from_entity_to_orm(entity: History) -> HistoryModel:
        return HistoryModel(**HistoryDTO.from_entity_to_dict(entity))
