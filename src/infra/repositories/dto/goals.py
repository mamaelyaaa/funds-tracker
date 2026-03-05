from domain.goals.dto import GoalDTO
from domain.goals.entities import Goal
from domain.goals.values import GoalId
from domain.users.values import UserId
from domain.values import Title, Money
from infra.models.goals import GoalModel


class GoalOrmDTO:

    @staticmethod
    def from_orm_to_entity(model: GoalModel) -> Goal:
        return Goal(
            id=GoalId(model.id),
            user_id=UserId(model.user_id),
            title=Title(model.title),
            target_amount=Money(model.target_amount),
            current_amount=Money(model.current_amount),
            status=model.status,
            deadline=model.deadline if model.deadline else None,
            created_at=model.created_at,
        )

    @staticmethod
    def from_entity_to_orm(entity: Goal) -> GoalModel:
        return GoalModel(**GoalDTO.from_entity_to_dict(entity))
