from domain.accounts.values import AccountId, Money
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
            delta=float(model.delta),
            balance=Money(model.balance),
            is_monthly_closing=model.is_monthly_closing,
            created_at=model.created_at,
        )

    @staticmethod
    def from_entity_to_orm(entity: History) -> HistoryModel:
        return HistoryModel(**HistoryDTO.from_entity_to_dict(entity))
