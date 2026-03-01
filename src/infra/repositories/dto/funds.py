from domain.accounts.dto import AccountDTO
from domain.accounts.entity import Account
from domain.accounts.values import AccountId, Title, Money
from domain.funds.dto import FundDTO
from domain.funds.entity import Fund
from domain.funds.values import FundId
from domain.users.values import UserId
from infra.models import AccountModel, FundModel


class FundOrmDTO(FundDTO):

    @staticmethod
    def from_orm_to_entity(model: FundModel) -> Fund:
        return Fund(
            id=FundId(model.id),
            user_id=UserId(model.user_id),
            total_amount=Money(model.total_amount),
            start_date=model.start_date,
            end_date=model.end_date,
            created_at=model.created_at,
        )

    @staticmethod
    def from_entity_to_orm(entity: Fund) -> FundModel:
        return FundModel(**FundDTO.from_entity_to_dict(entity))
