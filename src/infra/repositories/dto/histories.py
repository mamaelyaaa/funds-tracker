from domain.accounts.values import AccountId
from domain.histories.dto import HistoryDTO
from domain.histories.entities import History
from domain.histories.values import HistoryId
from infra.models import HistoryModel


class HistoryOrmDTO(HistoryDTO):

    @staticmethod
    def from_orm_to_entity(model: HistoryModel) -> History:
        return History(
            id=HistoryId(model.id),
            account_id=AccountId(model.account_id),
            balance=model.balance,
            created_at=model.created_at,
        )

    @staticmethod
    def from_entity_to_orm(entity: History) -> HistoryModel:
        return HistoryModel(**HistoryDTO.from_entity_to_dict(entity))
