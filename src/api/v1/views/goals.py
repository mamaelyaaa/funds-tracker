from fastapi import APIRouter, Depends, status

from api.schemas import (
    BaseResponseDetailSchema,
    BaseExceptionSchema,
    PaginationMetaSchema,
    PaginationDep,
)
from api.v1.dependencies.auth import http_bearer, AccessTokenDep
from api.v1.dependencies.goals import GoalServiceDep
from api.v1.schemas.goals import CreateGoalSchema, GoalDetailSchema, UpdateGoalSchema
from domain.commands import PaginationCommand
from domain.goals.command import (
    CreateGoalCommand,
    UpdateGoalPartiallyCommand,
    GetGoalCommand,
    GetGoalsCommand,
)
from domain.goals.dto import GoalDTO

router = APIRouter(
    prefix="/goals",
    tags=["Цели🎯"],
    dependencies=[Depends(http_bearer)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": BaseExceptionSchema,
            "description": "Пользователь не авторизован",
        },
    },
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
            "description": "'Не найден пользователь' ИЛИ 'Не найден счёт пользователя'",
        },
    },
)
async def create_goal(
    goals_service: GoalServiceDep,
    schema: CreateGoalSchema,
    user_id: AccessTokenDep,
):
    """
    Создание цели пользователя
    """

    goal = await goals_service.create_goal(
        command=CreateGoalCommand(
            user_id=user_id,
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
    response_model=BaseResponseDetailSchema[
        list[GoalDetailSchema], PaginationMetaSchema
    ],
)
async def get_user_goals(
    goals_service: GoalServiceDep,
    user_id: AccessTokenDep,
    pagination: PaginationDep,
):
    """Получение всех целей пользователя"""
    goals, pagination_meta = await goals_service.get_user_goals(
        command=GetGoalsCommand(
            user_id=user_id,
            pagination=PaginationCommand(**pagination.model_dump()),
        )
    )

    return BaseResponseDetailSchema(
        detail=[GoalDTO.from_entity_to_dict(goal) for goal in goals],
        message="Получен список целей пользователя",
        metadata=pagination_meta,
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
    goals_service: GoalServiceDep,
    user_id: AccessTokenDep,
    goal_id: str,
):
    """Получение конкретной цели пользователя"""

    goal = await goals_service.get_user_goal(
        command=GetGoalCommand(goal_id=goal_id, user_id=user_id)
    )
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
    goals_service: GoalServiceDep,
    schema: UpdateGoalSchema,
    user_id: AccessTokenDep,
    goal_id: str,
):
    """Обновление цели пользователя"""

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
    goals_service: GoalServiceDep,
    user_id: AccessTokenDep,
    goal_id: str,
):
    """Удаление цели пользователя"""

    await goals_service.delete_goal(
        command=GetGoalCommand(goal_id=goal_id, user_id=user_id)
    )
    return
