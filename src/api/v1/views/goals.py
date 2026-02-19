from fastapi import APIRouter, Depends, status

from api.schemas import BaseResponseDetailSchema
from api.v1.schemas.goals import CreateGoalSchema, GoalDetailSchema, UpdateGoalSchema
from domain.accounts.commands import GetAccountCommand
from domain.accounts.service import AccountServiceDep
from domain.goals.command import CreateGoalCommand, UpdateGoalPartiallyCommand
from domain.goals.service import GoalsServiceDep
from domain.users.dependencies import get_user

router = APIRouter(
    prefix="/users/{user_id}/goals",
    tags=["Цели🎯"],
    dependencies=[Depends(get_user)],
)


@router.post(
    "",
    response_model=BaseResponseDetailSchema[GoalDetailSchema, dict],
    status_code=status.HTTP_201_CREATED,
)
async def create_goal(
    account_service: AccountServiceDep,
    goals_service: GoalsServiceDep,
    schema: CreateGoalSchema,
    user_id: str,
):
    if schema.account_id:
        account = await account_service.find_account_by_id(
            command=GetAccountCommand(user_id=user_id, account_id=schema.account_id)
        )
    else:
        account = None

    goal = await goals_service.create_goal(
        command=CreateGoalCommand(
            user_id=user_id,
            account=account,
            **schema.model_dump(exclude={"account", "account_id"}),
        )
    )
    return BaseResponseDetailSchema(
        detail=GoalDetailSchema.from_entity(goal),
        message="Цель успешно создана",
        metadata={},
    )


@router.get("", response_model=BaseResponseDetailSchema[list[GoalDetailSchema], dict])
async def get_user_goals(
    goals_service: GoalsServiceDep,
    user_id: str,
):
    goals = await goals_service.get_user_goals(user_id=user_id)
    return BaseResponseDetailSchema(
        detail=[GoalDetailSchema.from_entity(goal) for goal in goals],
        message="Получен список целей пользователя",
        metadata={},
    )


@router.get(
    "/{goal_id}", response_model=BaseResponseDetailSchema[GoalDetailSchema, dict]
)
async def get_user_goal(
    goals_service: GoalsServiceDep,
    user_id: str,
    goal_id: str,
):
    goal = await goals_service.get_user_goal(goal_id=goal_id)
    return BaseResponseDetailSchema(
        detail=GoalDetailSchema.from_entity(goal),
        message="Цель получена",
        metadata={},
    )


@router.patch(
    "/{goal_id}", response_model=BaseResponseDetailSchema[GoalDetailSchema, dict]
)
async def update_user_goal(
    goals_service: GoalsServiceDep,
    account_service: AccountServiceDep,
    schema: UpdateGoalSchema,
    user_id: str,
    goal_id: str,
):
    account = None
    if schema.account_id:
        account = await account_service.find_account_by_id(
            command=GetAccountCommand(user_id=user_id, account_id=schema.account_id)
        )

    upd_goal = await goals_service.update_goal_partially(
        command=UpdateGoalPartiallyCommand(
            user_id=user_id,
            goal_id=goal_id,
            account=account,
            **schema.model_dump(exclude={"account", "account_id"}),
        )
    )
    return BaseResponseDetailSchema(
        detail=GoalDetailSchema.from_entity(upd_goal),
        message="Цель успешно обновлена",
        metadata={},
    )


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def get_user_goal(
    goals_service: GoalsServiceDep,
    user_id: str,
    goal_id: str,
):
    await goals_service.delete_goal(goal_id=goal_id)
    return
