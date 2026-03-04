from datetime import datetime, timedelta

from infra.repositories.funds import FundRepositoryDep
from infra.repositories.histories import HistoryRepositoryDep
from .entity import Fund
from .protocol import FundRepositoryProtocol
from .values import FundStatus
from ..histories.protocols import HistoryRepositoryProtocol

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
        history_repo: HistoryRepositoryProtocol,
        # fund_distribution_repo: FundDistributionRepositoryProtocol,
        # fund_rule_repo: FundRuleRepositoryProtocol,
    ):
        self._fund_repo = fund_repo
        self._history_repo = history_repo
        # self._fund_distribution_repo = fund_distribution_repo

    async def create_or_update_period(self, user_id: str, end_date: datetime) -> None:
        """Создаем новый период или обновляем существующий"""

        open_fund = await self._fund_repo.get_last_opened(user_id)

        if open_fund:
            await self._update_fund(fund=open_fund, end_date=end_date)
        else:
            await self._create_new_fund(user_id=user_id, end_date=end_date)

    async def _create_new_fund(self, user_id: str, end_date: datetime) -> None:
        """
        Создаем новый период для остатка

        Если до этого закрытых периодов не было, то start_date становится значением даты создания первой записи
        Если до этого был закрытый период, то start_date = last_closed_date + 1
        """

        last_closed_fund = await self._fund_repo.get_last_closed(user_id)
        start_date = (
            last_closed_fund.end_date + timedelta(days=1)
            if last_closed_fund
            else end_date
        )

        total_amount = await self._history_repo.get_sum_delta_in_period(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        fund = Fund.create(
            user_id=user_id,
            total_amount=total_amount,
            status=FundStatus.OPEN,
            start_date=start_date,
            end_date=end_date,
        )
        await self._fund_repo.save(fund)

    async def _update_fund(self, fund: Fund, end_date: datetime) -> None:
        """Обновляет существующий остаток"""

        new_total = await self._history_repo.get_sum_delta_in_period(
            user_id=fund.user_id.as_generic_type(),
            end_date=end_date,
            start_date=fund.start_date,
        )
        data = {"total_amount": new_total, "end_date": end_date}

        await self._fund_repo.update(
            fund_id=fund.id.as_generic_type(),
            user_id=fund.user_id.as_generic_type(),
            upd_data=data,
        )

    # async def update_fund(self, command: UpdateFundCommand) -> None:
    #     """Обновляет запись об остатке"""
    #
    #     # Проверяем существует ли открытая запись в БД
    #     opened_fund = await self._fund_repo.get_by_user_id(
    #         user_id=command.user_id, status=FundStatus.OPEN
    #     )
    #
    #     if not opened_fund:
    #         raise ...
    #
    #     if opened_fund.total_amount != command.new_amount:
    #         opened_fund.update_amount(new_balance=command.new_amount)
    #
    #     await self._fund_repo.update(
    #         user_id=command.user_id,
    #         fund_id=opened_fund.id.as_generic_type(),
    #         upd_data=FundDTO.from_entity_to_dict(
    #             opened_fund, excludes=["id", "user_id"]
    #         ),
    #     )

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
    history_repo: HistoryRepositoryDep,
) -> FundService:
    return FundService(
        fund_repo=fund_repo,
        history_repo=history_repo,
        # account_repo=acc_repo,
        # fund_repo=fund_repo,
        # goal_repo=goal_repo
    )
