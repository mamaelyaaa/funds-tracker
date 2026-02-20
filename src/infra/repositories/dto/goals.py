from domain.accounts.values import AccountId, Title
from domain.goals.dto import GoalDTO
from domain.goals.entities import Goal
from domain.goals.values import GoalId, GoalPercentage
from domain.users.values import UserId
from infra.models.goals import GoalModel


class GoalOrmDTO:

    @staticmethod
    def from_orm_to_entity(model: GoalModel) -> Goal:
        return Goal(
            id=GoalId(model.id),
            user_id=UserId(model.user_id),
            account_id=AccountId(model.account_id) if model.account_id else None,
            title=Title(model.title),
            target_amount=model.target_amount,
            current_amount=model.current_amount,
            status=model.status,
            savings_percentage=GoalPercentage(model.savings_percentage),
            deadline=model.deadline if model.deadline else None,
            created_at=model.created_at,
        )

    @staticmethod
    def from_entity_to_orm(entity: Goal) -> GoalModel:
        return GoalModel(**GoalDTO.from_entity_to_dict(entity))


# class GoalDTO(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#
#     id: str
#     user_id: str
#     account_id: Optional[str]
#
#     title: str
#     target_amount: float
#     current_amount: float
#
#     status: GoalStatus
#     deadline: Optional[datetime]
#     savings_percentage: Optional[float]

# @staticmethod
# def to_orm(goal: Goal) -> GoalModel:
#     return GoalModel(
#         id=goal.id.as_generic_type(),
#         user_id=goal.user_id.as_generic_type(),
#         account_id=goal.account_id.as_generic_type() if goal.account_id else None,
#         title=goal.title.as_generic_type(),
#         target_amount=goal.target_amount,
#         deadline=goal.deadline,
#         savings_percentage=goal.savings_percentage.as_generic_type(),
#         status=goal.status,
#         current_amount=goal.current_amount,
#         created_at=goal.created_at,
#     )
#
# @staticmethod
# def to_entity(goal_model: GoalModel) -> Goal:
#     data = {**GoalDTO.model_validate(goal_model).model_dump()}
#     data.update(
#         id=GoalId(goal_model.id),
#         user_id=UserId(goal_model.user_id),
#         account_id=(
#             AccountId(goal_model.account_id) if goal_model.account_id else None
#         ),
#         title=Title(goal_model.title),
#         savings_percentage=(
#             GoalPercentage(goal_model.savings_percentage)
#             if goal_model.savings_percentage
#             else None
#         ),
#     )
#     return Goal(**data)
