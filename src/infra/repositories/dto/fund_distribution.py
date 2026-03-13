from domain.accounts.values import AccountId
from domain.funds.dto import FundDistDTO
from domain.funds.entity import FundDistribution
from domain.funds.values import FundId, FundDistributionId, FundRuleType
from domain.goals.values import GoalId
from domain.values import Money, Percent
from infra.models.funds import FundDistributionModel


class FundDistOrmDTO(FundDistDTO):

    @staticmethod
    def from_orm_to_entity(model: FundDistributionModel) -> FundDistribution:
        return FundDistribution(
            id=FundDistributionId(model.id),
            fund_id=FundId(model.fund_id),
            reserve_id=(
                AccountId(model.reserve_id)
                if model.reserve_type == FundRuleType.ACCOUNT
                else GoalId(model.reserve_id)
            ),
            reserve_type=model.reserve_type,
            amount=Money(model.amount),
            percent_applied=Percent(model.percent_applied),
            created_at=FundDistDTO.ensure_utc(model.created_at),
        )

    @staticmethod
    def from_entity_to_orm(entity: FundDistribution) -> FundDistributionModel:
        return FundDistributionModel(**FundDistDTO.from_entity_to_dict(entity))
