from infra.repositories.funds import FundRepositoryDep
from .commands import (
    # CreateManyAllocationsCommand,
    AllocateFundCommand,
    CreateFundCommand,
    UpdateFundCommand,
)
from .dto import FundDTO
from .entity import Fund
from .protocol import (
    FundRepositoryProtocol,
    # FundRuleRepositoryProtocol,
)
from .values import FundStatus

# class FundRulesService:
#     """Сервис работы с распределением остатка по процентам"""
#
#     def __init__(
#         self,
#         fund_rule_repo: FundRuleRepositoryProtocol,
#         account_repo: AccountRepositoryProtocol,
#         goal_repo: GoalsRepositoryProtocol,
#     ):
#         self._fund_rule_repo = fund_rule_repo
#         self._account_repo = account_repo
#         self._goal_repo = goal_repo
#
#     async def _check_reserve_id(
#         self, reserve_id: str, user_id: str, reserve_type: FundRuleType
#     ) -> None:
#         """Получает необходимый резерв для остатка благодаря типу"""
#
#         if reserve_type == FundRuleType.ACCOUNT:
#             if not await self._account_repo.check_exists_by_id(user_id, reserve_id):
#                 raise AccountNotFoundException
#
#         elif reserve_type == FundRuleType.GOAL:
#             if not await self._goal_repo.check_exists_by_id(user_id, reserve_id):
#                 raise GoalNotFoundException
#         else:
#             raise ...
#
#     async def _create_or_update_funds_rules(
#         self, command: CreateAllocationCommand
#     ) -> FundRule:
#         """Создает распределение для резерва с процентами"""
#
#         # Проверка на корректность "резерва"
#
#         await self._check_reserve_id(
#             user_id=command.user_id,
#             reserve_type=command.reserve_type,
#             reserve_id=command.reserve_id,
#         )
#
#         exists_fund_rule = await self._fund_rule_repo.get_by_user_and_reserve_id(
#             user_id=command.user_id, reserve_id=command.reserve_id
#         )
#         if exists_fund_rule:
#             pass
#
#         fund = FundRule.create(
#             user_id=command.user_id,
#             reserve_id=command.reserve_id,
#             reserve_type=command.reserve_type,
#             percent=command.percent,
#         )
#         return fund
#
#     async def allocate_reserves_with_percentage(
#         self, command: CreateManyAllocationsCommand
#     ):
#         pass


class FundService:

    def __init__(
        self,
        fund_repo: FundRepositoryProtocol,
        # fund_distribution_repo: FundDistributionRepositoryProtocol,
        # fund_rule_repo: FundRuleRepositoryProtocol,
        # account_repo: AccountRepositoryProtocol,
        # goal_repo: GoalsRepositoryProtocol,
    ):
        # super().__init__(
        #     fund_rule_repo=fund_rule_repo,
        #     account_repo=account_repo,
        #     goal_repo=goal_repo,
        # )
        self._fund_repo = fund_repo
        # self._fund_distribution_repo = fund_distribution_repo

    async def create_fund(self, command: CreateFundCommand) -> None:
        fund = Fund.create(
            user_id=command.user_id,
            total_amount=0,
            start_date=command.start_date,
            end_date=command.end_date,
            status=FundStatus.OPEN,
        )
        await self._fund_repo.save(fund)
        return

    async def update_fund(self, command: UpdateFundCommand) -> None:
        """Создает или обновляет запись об остатке"""

        # Проверяем существует ли открытая запись в БД
        opened_fund = await self._fund_repo.get_by_user_id(
            user_id=command.user_id, status=FundStatus.OPEN
        )

        if not opened_fund:
            raise ...

        if opened_fund.total_amount != command.new_amount:
            opened_fund.update_amount(new_balance=command.new_amount)

        await self._fund_repo.update(
            user_id=command.user_id,
            fund_id=opened_fund.id.as_generic_type(),
            upd_data=FundDTO.from_entity_to_dict(
                opened_fund, excludes=["id", "user_id"]
            ),
        )

        # for reserve in command.reserves:
        #
        #     fund_dist = FundDistribution.create(
        #         fund_id=fund.id.as_generic_type(),
        #         reserve_id=reserve.reserve_id,
        #         reserve_type=reserve.reserve_type,
        #         amount=reserve.amount,
        #         percent_applied=reserve.percent_applied,
        #     )
        #
        # return fund

    # async def allocate_new_funds(self, command: AllocateFundCommand):
    #     """Сохраняет распределение об остатке за период"""
    #
    #     # 1. Выбираются нужные счета/цели и их проценты
    #     # 2. Получаем накопленный остаток за текущий период (он создается фоново при обновлении
    #
    #     # Получаем крайний накопленный остаток
    #
    #     last_fund = await self._fund_repo.get_last_opened(user_id=command.user_id)
    #
    #     # if not last_fund:
    #     #     raise FundNotExistsException
    #
    #     # Получаем все резервы с процентами
    #
    #     ...
    #
    #     # Закрываем текущее распределение остатка и создаем записи в fund-distribution
    #
    #     last_fund.update_status(new_status=FundStatus.CLOSED)
    #     # await self._fund_repo.update(
    #     #     user_id=command.user_id,
    #     #     fund_id=last_fund.id.as_generic_type(),
    #     #     upd_data={"status": FundStatus.CLOSED},
    #     # )
    #     ...
    #
    # async def get_actual_funds(self, user_id: str) -> Fund:
    #     """Получает текущий накопленный остаток"""
    #
    #     funds = await self._fund_repo.get_by_user_id(user_id)
    #     if not funds:
    #         raise
    #     return funds


def get_fund_service(
    # acc_repo: AccountRepositoryDep,
    # goal_repo: GoalsRepositoryDep,
    fund_repo: FundRepositoryDep,
) -> FundService:
    return FundService(
        fund_repo=fund_repo
        # account_repo=acc_repo,
        # fund_repo=fund_repo,
        # goal_repo=goal_repo
    )
