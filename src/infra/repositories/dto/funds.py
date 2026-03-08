from domain.funds.dto import FundDTO
from domain.funds.entity import Fund
from domain.funds.values import FundId
from domain.users.values import UserId
from domain.values import Money
from infra.models import FundModel


class FundOrmDTO(FundDTO):

    @staticmethod
    def from_orm_to_entity(model: FundModel) -> Fund:
        return Fund(
            id=FundId(model.id),
            user_id=UserId(model.user_id),
            total_amount=Money(model.total_amount),
            start_date=FundDTO._ensure_utc(model.start_date),
            end_date=FundDTO._ensure_utc(model.end_date),
            created_at=FundDTO._ensure_utc(model.created_at),
        )

    @staticmethod
    def from_entity_to_orm(entity: Fund) -> FundModel:
        return FundModel(**FundDTO.from_entity_to_dict(entity))
