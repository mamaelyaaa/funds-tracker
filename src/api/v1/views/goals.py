from fastapi import APIRouter, Depends, status

from api.schemas import BaseResponseDetailSchema, BaseExceptionSchema
from api.v1.schemas.goals import CreateGoalSchema, GoalDetailSchema, UpdateGoalSchema
from api.v1.views.accounts import AccountServiceDep
from domain.accounts.commands import GetAccountCommand
from domain.goals.command import CreateGoalCommand, UpdateGoalPartiallyCommand
from domain.goals.dto import GoalDTO
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
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": BaseExceptionSchema,
            "description": "Некорректные входные данные",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": BaseExceptionSchema,
            "description": "'Не найден пользователь' ИЛИ "
            "'Не найден счёт пользователя' при попытке связать с целью",
        },
    },
)
async def create_goal(
    account_service: AccountServiceDep,
    goals_service: GoalsServiceDep,
    schema: CreateGoalSchema,
    user_id: str,
):
    """
    Создание цели пользователя

    1. Если к счёту будет привязан аккаунт, то текущая сумма цели будет равна балансу аккаунта
    2. Если id счёта будет некорректен - 404 ошибка
    3. Если будет привязан несуществующий счёт пользователя - 404 ошибка
    """

    # if schema.account_id:
    #     account = await account_service.find_account_by_id(
    #         command=GetAccountCommand(user_id=user_id, account_id=schema.account_id)
    #     )
    # else:
    #     account = None

    goal = await goals_service.create_goal(
        command=CreateGoalCommand(
            user_id=user_id,
            # account=account,
            **schema.model_dump(exclude={"user_id"}),
        )
    )
    return BaseResponseDetailSchema(
        detail=GoalDTO.from_entity_to_dict(goal),
        message="Цель успешно создана",
        metadata={},
    )


@router.get(
    "",
    response_model=BaseResponseDetailSchema[list[GoalDetailSchema], dict],
)
async def get_user_goals(
    goals_service: GoalsServiceDep,
    user_id: str,
):
    """Получение всех целей пользователя"""
    goals = await goals_service.get_user_goals(user_id=user_id)
    return BaseResponseDetailSchema(
        detail=[GoalDTO.from_entity_to_dict(goal) for goal in goals],
        message="Получен список целей пользователя",
        metadata={},
    )


@router.get(
    "/{goal_id}",
    response_model=BaseResponseDetailSchema[GoalDetailSchema, dict],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": BaseExceptionSchema,
            "description": "'Не найден пользователь' ИЛИ "
            "'Не найден счёт пользователя'",
        },
    },
)
async def get_user_goal(
    goals_service: GoalsServiceDep,
    user_id: str,
    goal_id: str,
):
    goal = await goals_service.get_user_goal(goal_id=goal_id, user_id=user_id)
    return BaseResponseDetailSchema(
        detail=GoalDTO.from_entity_to_dict(goal),
        message="Цель получена",
        metadata={},
    )


@router.patch(
    "/{goal_id}",
    response_model=BaseResponseDetailSchema[GoalDetailSchema, dict],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": BaseExceptionSchema,
            "description": "'Не найден пользователь' ИЛИ "
            "'Не найден счёт пользователя'",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": BaseExceptionSchema,
            "description": "Некорректные входные данные",
        },
    },
)
async def update_user_goal(
    goals_service: GoalsServiceDep,
    account_service: AccountServiceDep,
    schema: UpdateGoalSchema,
    user_id: str,
    goal_id: str,
):
    # account = None
    # if schema.account_id:
    #     account = await account_service.find_account_by_id(
    #         command=GetAccountCommand(user_id=user_id, account_id=schema.account_id)
    #     )

    upd_goal = await goals_service.update_goal_partially(
        command=UpdateGoalPartiallyCommand(
            user_id=user_id,
            goal_id=goal_id,
            **schema.model_dump(),
        )
    )
    return BaseResponseDetailSchema(
        detail=GoalDTO.from_entity_to_dict(upd_goal),
        message="Цель успешно обновлена",
        metadata={},
    )


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": BaseExceptionSchema,
            "description": "'Не найден пользователь' ИЛИ "
            "'Не найден счёт пользователя'",
        },
    },
)
async def get_user_goal(
    goals_service: GoalsServiceDep,
    user_id: str,
    goal_id: str,
):
    await goals_service.delete_goal(goal_id=goal_id, user_id=user_id)
    return
